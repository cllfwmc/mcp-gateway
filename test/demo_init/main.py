from mcp.server.fastmcp import FastMCP
import argparse

# ---------- 1. 实例化 + 注册工具 ----------
mcp = FastMCP("SingleTransport", json_response=True)

@mcp.tool()
def greet(name: str = "World") -> str:
    return f"Hello, {name}!"

# ---------- 2. 命令行选协议 ----------
parser = argparse.ArgumentParser()
parser.add_argument(
    "--transport",
    choices=["stdio", "sse", "streamable-http"],
    default="stdio",
    help="要启动的传输协议",
)
args = parser.parse_args()

# ---------- 3. 直接调 run() ----------
# 注意：这里**不要再**包 asyncio.run()！
if args.transport == "stdio":
    mcp.run("stdio")
elif args.transport == "sse":
    mcp.run("sse")
elif args.transport == "streamable-http":
    mcp.run("streamable-http")


# COMMAND: E:\学术\杂\小项目\mcp-gateway\.venv\Scripts\python.exe
# ARGUMENTS: "E:\学术\杂\小项目\mcp-gateway\test\demo_init\main.py" --transport stdio