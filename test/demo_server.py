from mcp.server.fastmcp import FastMCP
import mcp.types as types

mcp = FastMCP("StatefulServer", json_response=True)   # 默认 stateless_http=False

@mcp.tool()
def greet(name: str = "World") -> str:
    return f"Hello, {name}!"

if __name__ == "__main__":
    mcp.run(transport="streamable-http")   # 有状态，但客户端每次换新 ID 即可