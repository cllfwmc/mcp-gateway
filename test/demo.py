# server.py
import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from mcp.server.sse import SseServerTransport
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# ---------------- 1. 创建 MCP Server ----------------
server = Server("demo")

@server.list_tools()
async def list_tools():
    return [Tool(name="add", description="add two numbers", inputSchema={
        "type": "object",
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "required": ["a", "b"]
    })]

@server.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "add":
        total = arguments["a"] + arguments["b"]
        return [TextContent(type="text", text=str(total))]
    raise ValueError(f"Unknown tool {name}")

# ---------------- 2. 创建 SSE 传输层 ----------------
# 注意：消息路径可以挂载多条，这里我们把 /mcp 和 /messages 都指向同一个 handle_post_message
sse = SseServerTransport("/messages/")

async def handle_sse(scope, receive, send):
    async with sse.connect_sse(scope, receive, send) as (reader, writer):
        await server.run(reader, writer, server.create_initialization_options())

# ---------------- 3. 组装路由 ----------------
routes = [
    Route("/sse", endpoint=handle_sse),               # SSE 长连接
    Mount("/messages", app=sse.handle_post_message),  # 官方默认 POST 端点
    Mount("/mcp", app=sse.handle_post_message),       # 额外暴露的 JSON-RPC 端点
]

app = Starlette(routes=routes)

# ---------------- 4. 启动 ----------------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)