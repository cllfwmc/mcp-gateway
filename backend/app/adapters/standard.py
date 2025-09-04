from typing import Any, Dict

from .base import MCPAdapter


class StandardMCPAdapter(MCPAdapter):
	async def to_streamable_http(self, spec: Dict[str, Any]) -> Dict[str, Any]:
		return {**spec, "protocol": "streamable-http"}

	async def to_sse(self, spec: Dict[str, Any]) -> Dict[str, Any]:
		return {**spec, "protocol": "sse"}

	async def to_stdio(self, spec: Dict[str, Any]) -> Dict[str, Any]:
		return {**spec, "protocol": "stdio"}
