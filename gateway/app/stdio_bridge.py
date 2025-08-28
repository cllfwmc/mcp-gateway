from __future__ import annotations
import sys
import json
import asyncio
import httpx
from .config import ConfigLoader
from .transforms import get as get_transform


async def handle_line(line: str) -> None:
    cfg = ConfigLoader.get()
    servers = cfg.mcp_servers
    if not servers:
        sys.stdout.write(json.dumps({"error": "No MCP servers configured"}) + "\n")
        sys.stdout.flush()
        return

    try:
        payload = json.loads(line)
    except Exception as e:  # noqa: BLE001
        sys.stdout.write(json.dumps({"error": f"Invalid JSON: {e}"}) + "\n")
        sys.stdout.flush()
        return

    # Optional: select server via payload.meta.server
    server_name = payload.pop("__server__", None) or next(iter(servers.keys()))
    if server_name not in servers:
        sys.stdout.write(json.dumps({"error": f"Server '{server_name}' not found"}) + "\n")
        sys.stdout.flush()
        return

    upstream = servers[server_name]

    req_transform = upstream.requestTransform or "default"
    req_func = get_transform(req_transform) or get_transform("default")
    if req_func:
        try:
            payload = req_func(payload)
        except Exception as e:  # noqa: BLE001
            sys.stdout.write(json.dumps({"error": f"requestTransform '{req_transform}' failed: {e}"}) + "\n")
            sys.stdout.flush()
            return

    resp_transform = upstream.responseTransform or "default"
    resp_func = get_transform(resp_transform) or get_transform("default")

    async with httpx.AsyncClient(timeout=httpx.Timeout(None)) as client:
        async with client.stream("POST", upstream.url, json=payload, headers=upstream.headers or {}) as resp:
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
                    try:
                        obj = json.loads(ln.decode("utf-8"))
                        if resp_func:
                            obj = resp_func(obj)
                        sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
                    except Exception:
                        sys.stdout.write(ln.decode("utf-8", errors="ignore") + "\n")
                    sys.stdout.flush()
            if buffer:
                try:
                    obj = json.loads(buffer.decode("utf-8"))
                    if resp_func:
                        obj = resp_func(obj)
                    sys.stdout.write(json.dumps(obj, ensure_ascii=False) + "\n")
                except Exception:
                    sys.stdout.write(buffer.decode("utf-8", errors="ignore"))
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
