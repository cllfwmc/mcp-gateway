from __future__ import annotations
from typing import Optional
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import StreamingResponse
import httpx
from ..config import ConfigLoader

router = APIRouter()


def to_sse(data: bytes) -> bytes:
    # naive framing: each upstream chunk -> one data event line
    return b"data: " + data.replace(b"\n", b" ") + b"\n\n"


@router.get("/sse")
async def sse_bridge(request: Request, server: Optional[str] = None) -> StreamingResponse:
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

    body = await request.body()
    incoming_headers = dict(request.headers)
    for k in ["host", "content-length"]:
        incoming_headers.pop(k, None)
    merged_headers = {**(upstream.headers or {}), **incoming_headers}

    async def event_stream():
        timeout = httpx.Timeout(None)
        async with httpx.AsyncClient(timeout=timeout) as client:
            async with client.stream("POST", upstream.url, headers=merged_headers, content=body) as resp:
                resp.raise_for_status()
                async for chunk in resp.aiter_raw():
                    if chunk:
                        yield to_sse(chunk)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
