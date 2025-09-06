import requests
import json
from urllib.parse import urlencode

GATEWAY_BASE = "http://127.0.0.1:8000"
MCP_ENDPOINT = f"{GATEWAY_BASE}/mcp"
SSE_ENDPOINT = f"{GATEWAY_BASE}/sse"


def mcp_request(method: str, params: dict | None = None, session_id: str | None = None, is_notification: bool = False):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if session_id:
        headers["mcp-session-id"] = session_id

    payload: dict = {"jsonrpc": "2.0", "method": method}
    if not is_notification:
        payload["id"] = "1"
    if params is not None:
        payload["params"] = params

    resp = requests.post(MCP_ENDPOINT, headers=headers, json=payload, timeout=10)
    return resp


def init_session() -> str | None:
    init_params = {
        "protocolVersion": "2025-03-26",
        "capabilities": {},
        "clientInfo": {"name": "sse-client", "version": "0.1.0"},
    }
    r = mcp_request("initialize", init_params)
    sid = r.headers.get("mcp-session-id")
    # notifications/initialized (no id)
    mcp_request("notifications/initialized", session_id=sid, is_notification=True)
    return sid


def open_sse(session_id: str | None, payload: dict | None = None):
    params = {}
    if payload is not None:
        params["q"] = json.dumps(payload, ensure_ascii=False)
    url = SSE_ENDPOINT + ("?" + urlencode(params) if params else "")

    headers = {
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
    }
    if session_id:
        headers["mcp-session-id"] = session_id

    with requests.get(url, headers=headers, stream=True, timeout=30) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines(decode_unicode=True):
            if not line:
                continue
            print(line)


if __name__ == "__main__":
    sid = init_session()
    print("session:", sid)
    # Example: open SSE and then send a ping request over POST path to trigger response
    open_sse(sid)
