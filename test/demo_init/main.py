from mcp.server.fastmcp import FastMCP  
from mcp.server.auth.provider import AccessToken, TokenVerifier  
from mcp.server.auth.settings import AuthSettings  
from pydantic import AnyHttpUrl  
import argparse  
  
# 实现 TokenVerifier  
class MyTokenVerifier(TokenVerifier):  
    async def verify_token(self, token: str) -> AccessToken | None:  
        # 在这里实现你的 token 验证逻辑  
        # 例如：验证 JWT token，查询数据库等  
        if token == "token_test":  # 替换为实际验证逻辑  
            return AccessToken(  
                token=token,  
                client_id="my_client",  
                scopes=["user"],  
                expires_at=None  # 不过期，或者设置具体时间戳  
            )  
        return None  
  
# 创建 FastMCP 实例并配置认证  
mcp = FastMCP(  
    "SingleTransport",   
    json_response=True,  
    # token_verifier=MyTokenVerifier(),  
    # auth=AuthSettings(  
    #     issuer_url=AnyHttpUrl("http://localhost:8000"),  
    #     resource_server_url=AnyHttpUrl("http://localhost:8000"),  
    #     required_scopes=["user"],  
    # )  
)  
  
@mcp.tool()  
def greet(name: str = "World") -> str:  
    return f"Hello, {name}!"  
  
# 其余代码保持不变  
parser = argparse.ArgumentParser()  
parser.add_argument(  
    "--transport",  
    choices=["stdio", "sse", "streamable-http"],  
    default="stdio",  
    help="要启动的传输协议",  
)  
args = parser.parse_args()  
  
if args.transport == "stdio":  
    mcp.run("stdio")  
elif args.transport == "sse":  
    mcp.run("sse")  
elif args.transport == "streamable-http":  
    mcp.run("streamable-http")


# COMMAND: E:\学术\杂\小项目\mcp-gateway\.venv\Scripts\python.exe
# ARGUMENTS: "E:\学术\杂\小项目\mcp-gateway\test\demo_init\main.py" --transport stdio


# COMMAND: E:\学术\杂\小项目\mcp-gateway\.venv\Scripts\python.exe
# ARGUMENTS: "E:\学术\杂\小项目\mcp-gateway\test\demo_init\main.py" --transport stdio