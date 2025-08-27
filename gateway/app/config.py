from __future__ import annotations
from typing import Dict, Optional
from pydantic import BaseModel, Field
import os
import yaml


class MCPServer(BaseModel):
    type: str = Field(..., description="server type, e.g. streamable-http")
    url: str
    headers: Dict[str, str] | None = None


class ConfigSchema(BaseModel):
    mcpServers: Dict[str, MCPServer] = Field(default_factory=dict)

    @property
    def mcp_servers(self) -> Dict[str, MCPServer]:
        return self.mcpServers


class ConfigLoader:
    _instance: Optional[ConfigSchema] = None

    @classmethod
    def load(cls, path: Optional[str] = None) -> ConfigSchema:
        config_path = path or os.getenv("GATEWAY_CONFIG", "config.yaml")
        with open(config_path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        cfg = ConfigSchema(**data)
        cls._instance = cfg
        return cfg

    @classmethod
    def get(cls) -> ConfigSchema:
        if cls._instance is None:
            return cls.load()
        return cls._instance
