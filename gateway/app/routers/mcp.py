from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from ..config import ConfigLoader

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

    body = await request.body()

    # Prepare headers: merge configured headers and incoming headers (without host/content-length overrides)
    incoming_headers = dict(request.headers)
    for k in ["host", "content-length"]:
        incoming_headers.pop(k, None)
    merged_headers = {**(upstream.headers or {}), **incoming_headers}

    async def iter_stream():
        timeout = httpx.Timeout(None)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", upstream.url, headers=merged_headers, content=body) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_raw():
                    if chunk:
                        yield chunk

    return StreamingResponse(iter_stream(), media_type="application/json")
