from __future__ import annotations
from typing import Dict, Optional
from pydantic import BaseModel, Field
import os
import json
import threading
import yaml


def _interpolate_env(value: str) -> str:
    # Simple ${VAR} interpolation
    out = value
    for part in os.environ:
        token = "${" + part + "}"
        if token in out:
            out = out.replace(token, os.environ.get(part, ""))
    return out


class MCPServer(BaseModel):
    type: str = Field(..., description="server type, e.g. streamable-http")
    url: str
    headers: Dict[str, str] | None = None
    requestTransform: str | None = None
    responseTransform: str | None = None


class ConfigSchema(BaseModel):
    mcpServers: Dict[str, MCPServer] = Field(default_factory=dict)

    @property
    def mcp_servers(self) -> Dict[str, MCPServer]:
        return self.mcpServers


class ConfigLoader:
    _instance: Optional[ConfigLoader] = None
    _lock = threading.Lock()

    def __init__(self, config_path: str):
        self.config_path = config_path
        self._config: ConfigSchema | None = None
        self._load()

    def _load(self) -> None:
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f) if self.config_path.endswith('.json') else yaml.safe_load(f) or {}
            else:
                data = {}
            
            # env interpolation for headers values
            servers = data.get("mcpServers", {}) or {}
            for _, srv in servers.items():
                headers = srv.get("headers") or {}
                for hk, hv in list(headers.items()):
                    if isinstance(hv, str):
                        headers[hk] = _interpolate_env(hv)
                srv["headers"] = headers
            
            self._config = ConfigSchema(**data)
            print(f"Config loaded successfully from {self.config_path}")
        except Exception as e:
            print(f"Error loading config: {e}")
            self._config = ConfigSchema()

    def _save(self) -> None:
        try:
            print(f"Starting to save config to {self.config_path}")
            if self._config is None:
                print("Config is None, skipping save")
                return
            data = {
                "mcpServers": {
                    name: {
                        "type": server.type,
                        "url": server.url,
                        "headers": server.headers,
                        "requestTransform": server.requestTransform,
                        "responseTransform": server.responseTransform
                    }
                    for name, server in self._config.mcpServers.items()
                }
            }
            print(f"Prepared data with {len(data['mcpServers'])} servers")
            # Write to temporary file first, then rename for atomic operation
            temp_path = self.config_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Wrote to temp file: {temp_path}")
            # Atomic rename
            if os.path.exists(self.config_path):
                os.replace(temp_path, self.config_path)
            else:
                os.rename(temp_path, self.config_path)
            print(f"Config saved successfully to {self.config_path}")
        except Exception as e:
            print(f"Error saving config: {e}")
            # Clean up temp file if it exists
            temp_path = self.config_path + ".tmp"
            if os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                    print(f"Cleaned up temp file: {temp_path}")
                except:
                    pass

    def get_config(self) -> ConfigSchema:
        return self._config

    def add_server(self, name: str, server: MCPServer) -> None:
        print(f"Adding server: {name}")
        with self._lock:
            if self._config is None:
                self._config = ConfigSchema()
            self._config.mcpServers[name] = server
            self._save()

    def remove_server(self, name: str) -> bool:
        print(f"Removing server: {name}")
        with self._lock:
            if self._config is None:
                return False
            if name in self._config.mcpServers:
                del self._config.mcpServers[name]
                self._save()
                return True
            return False

    def update_server_instance(self, name: str, server: MCPServer) -> bool:
        print(f"Updating server: {name}")
        with self._lock:
            if self._config is None:
                return False
            if name in self._config.mcpServers:
                self._config.mcpServers[name] = server
                self._save()
                return True
            return False

    def reload(self) -> None:
        self._load()

    @classmethod
    def load(cls, path: Optional[str] = None) -> ConfigLoader:
        config_path = path or os.getenv("GATEWAY_CONFIG", "config.json")
        if cls._instance is None:
            cls._instance = cls(config_path)
        return cls._instance

    @classmethod
    def get(cls) -> ConfigSchema:
        if cls._instance is None:
            cls.load()
        return cls._instance.get_config()

    @classmethod
    def add_server(cls, name: str, server: MCPServer) -> None:
        if cls._instance is None:
            cls.load()
        cls._instance.add_server(name, server)

    @classmethod
    def remove_server(cls, name: str) -> bool:
        if cls._instance is None:
            cls.load()
        return cls._instance.remove_server(name)

    @classmethod
    def update_server(cls, name: str, server: MCPServer) -> bool:
        if cls._instance is None:
            cls.load()
        return cls._instance.update_server_instance(name, server)

    @classmethod
    def reload(cls) -> None:
        if cls._instance is None:
            cls.load()
        cls._instance.reload()
