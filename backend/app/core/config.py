from functools import lru_cache
from pydantic import BaseModel
import os


class Settings(BaseModel):
	secret_key: str = os.getenv("MCP_GATEWAY_SECRET", "dev-secret-change-me")
	access_token: str | None = os.getenv("MCP_GATEWAY_TOKEN")
	cors_allow_origins: list[str] = (
		os.getenv("CORS_ALLOW_ORIGINS", "*").split(",") if os.getenv("CORS_ALLOW_ORIGINS") else ["*"]
	)
	mcp_config_dir: str = os.getenv("MCP_CONFIG_DIR", "configs")
	ui_path: str = os.getenv("UI_PATH", "ui")


@lru_cache
def get_settings() -> Settings:
	return Settings()
