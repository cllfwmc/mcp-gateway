from .demo_server import mcp

if __name__ == "__main__":
    mcp.run(transport="streamable-http")   # 有状态，但客户端每次换新 ID 即可