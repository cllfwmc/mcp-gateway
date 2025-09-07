from pydantic import BaseModel, Field
from mcp.server.fastmcp import Settings

# ---------------- 工具参数模型 ----------------
class GreetArgs(BaseModel):
    name: str = Field(default="World", description="要打招呼的对象")

# ---------------- 真正的 settings ----------------
def build_settings() -> Settings:
    """
    把 tools / resources / prompts 全部注册到一个 Settings 对象里，
    后面三个协议实例直接复用它即可。
    """
    settings = Settings()

    @settings.tool()
    def greet(args: GreetArgs) -> str:
        """向指定对象问好"""
        return f"Hello, {args.name}!"

    return settings