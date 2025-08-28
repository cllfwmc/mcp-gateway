from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import json
from ..config import ConfigLoader
from ..transforms import get as get_transform

router = APIRouter()


def to_sse(data: bytes) -> bytes:
    return b"data: " + data.replace(b"\n", b" ") + b"\n\n"


@router.get("/sse")
async def sse_bridge(request: Request, server: Optional[str] = None, q: Optional[str] = None) -> StreamingResponse:
    cfg = ConfigLoader.get()
    servers = cfg.mcp_servers
    if not servers:
        raise HTTPException(status_code=500, detail="No MCP servers configured")

    server_name = server or next(iter(servers.keys()))
    if server_name not in servers:
        raise HTTPException(status_code=404, detail=f"Server '{server_name}' not found")

    upstream = servers[server_name]
    if upstream.type != "streamable-http":
        raise HTTPException(status_code=400, detail="Only streamable-http is supported for /sse bridge")

    # Accept JSON payload via query param `q` or empty
    payload = None
    if q:
        try:
            payload = json.loads(q)
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"Invalid JSON in 'q': {e}")

    req_transform = upstream.requestTransform or "default"
    req_func = get_transform(req_transform) or get_transform("default")
    if payload is not None and req_func:
        try:
            payload = req_func(payload)
        except Exception as e:  # noqa: BLE001
            raise HTTPException(status_code=400, detail=f"requestTransform '{req_transform}' failed: {e}")

    incoming_headers = dict(request.headers)
    for k in ["host", "content-length"]:
        incoming_headers.pop(k, None)
    merged_headers = {**(upstream.headers or {}), **incoming_headers}

    async def event_stream():
        timeout = httpx.Timeout(None)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", upstream.url, headers=merged_headers, json=payload) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_raw():
                    if chunk:
                        yield to_sse(chunk)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
