from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import json
from ..config import ConfigLoader
from ..transforms import get as get_transform

router = APIRouter()


@router.post("/mcp")
async def proxy_mcp(request: Request, server: Optional[str] = None) -> Response:
    cfg = ConfigLoader.get()
    servers = cfg.mcp_servers
    if not servers:
        raise HTTPException(status_code=500, detail="No MCP servers configured")

    server_name = server or next(iter(servers.keys()))
    if server_name not in servers:
        raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")

    upstream = servers[server_name]
    if upstream.type != "streamable-http":
        raise HTTPException(status_code=400, detail="Only streamable-http is supported for /mcp proxy")

    # Parse JSON body and apply request transform if any
    try:
        payload = await request.json()
    except Exception:
        payload = None

    req_transform = upstream.requestTransform or "default"
    req_func = get_transform(req_transform) or get_transform("default")
    if payload is not None and req_func:
        try:
            payload = req_func(payload)
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"requestTransform '{req_transform}' failed: {e}")

    # Prepare headers
    incoming_headers = dict(request.headers)
    for k in ["host", "content-length"]:
        incoming_headers.pop(k, None)
    merged_headers = {**(upstream.headers or {}), **incoming_headers}

    resp_transform = upstream.responseTransform or "default"
    resp_func = get_transform(resp_transform) or get_transform("default")

    async def iter_stream():
        timeout = httpx.Timeout(None)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", upstream.url, headers=merged_headers, json=payload) as resp:
                resp.raise_for_status()
                buffer = b""
                async for chunk in resp.aiter_raw():
                    if not chunk:
                        continue
                    buffer += chunk
                    lines = buffer.split(b"\n")
                    buffer = lines[-1]
                    for ln in lines[:-1]:
                        if not ln:
                            continue
                        # Try NDJSON line transform; fallback passthrough
                        try:
                            obj = json.loads(ln.decode("utf-8"))
                            if resp_func:
                                obj = resp_func(obj)
                            out = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
                            yield out
                        except Exception:
                            # Non-JSON line; pass through with newline
                            yield ln + b"\n"
                # Flush tail
                if buffer:
                    try:
                        obj = json.loads(buffer.decode("utf-8"))
                        if resp_func:
                            obj = resp_func(obj)
                        yield (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8")
                    except Exception:
                        yield buffer

    return StreamingResponse(iter_stream(), media_type="application/json")
