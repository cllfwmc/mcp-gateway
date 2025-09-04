from typing import Any, Dict, Callable

from .base import MCPAdapter


class CustomMCPAdapter(MCPAdapter):
	def __init__(self, transform: Callable[[Dict[str, Any], str], Dict[str, Any]]):
		self._transform = transform

	async def to_streamable_http(self, spec: Dict[str, Any]) -> Dict[str, Any]:
		return self._transform(spec, "streamable-http")

	async def to_sse(self, spec: Dict[str, Any]) -> Dict[str, Any]:
		return self._transform(spec, "sse")

	async def to_stdio(self, spec: Dict[str, Any]) -> Dict[str, Any]:
		return self._transform(spec, "stdio")
