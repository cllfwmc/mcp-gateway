import subprocess
import json
import sys

# Runs the stdio bridge and communicates via stdin/stdout

def run_stdio(messages: list[dict]):
    # Ensure Python runs module gateway.app.stdio_bridge
    proc = subprocess.Popen(
        [sys.executable, "-m", "gateway.app.stdio_bridge"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )

    try:
        for msg in messages:
            line = json.dumps(msg, ensure_ascii=False)
            proc.stdin.write(line + "\n")
            proc.stdin.flush()
            # Read one response line per request (bridge emits NDJSON)
            out = proc.stdout.readline().strip()
            print(out)
    finally:
        proc.terminate()


if __name__ == "__main__":
    initialize = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "stdio-client", "version": "0.1.0"},
        },
    }
    initialized = {
        "jsonrpc": "2.0",
        "method": "notifications/initialized",
    }
    ping = {
        "jsonrpc": "2.0",
        "id": "2",
        "method": "ping",
    }

    run_stdio([initialize, initialized, ping])
