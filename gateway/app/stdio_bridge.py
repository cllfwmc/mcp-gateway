from __future__ import annotations
import sys
import json
import asyncio
import httpx
from .config import ConfigLoader


async def handle_line(line: str) -> None:
    cfg = ConfigLoader.get()
    servers = cfg.mcp_servers
    if not servers:
        sys.stdout.write(json.dumps({"error": "No MCP servers configured"}) + "\n")
        sys.stdout.flush()
        return
    server_name = next(iter(servers.keys()))
    upstream = servers[server_name]
    payload = json.loads(line)
    async with httpx.AsyncClient(timeout=httpx.Timeout(None)) as client:
        resp = await client.post(upstream.url, json=payload, headers=upstream.headers or {})
        resp.raise_for_status()
        text = resp.text
    sys.stdout.write(text + "\n")
    sys.stdout.flush()


async def main() -> None:
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)

    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            await handle_line(line.decode("utf-8").strip())
        except Exception as e:  # noqa: BLE001
            sys.stdout.write(json.dumps({"error": str(e)}) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    ConfigLoader.load()
    asyncio.run(main())
