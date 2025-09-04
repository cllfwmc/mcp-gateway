from abc import ABC, abstractmethod
from typing import Any, Dict


class MCPAdapter(ABC):
	@abstractmethod
	async def to_streamable_http(self, spec: Dict[str, Any]) -> Dict[str, Any]:
		...

	@abstractmethod
	async def to_sse(self, spec: Dict[str, Any]) -> Dict[str, Any]:
		...

	@abstractmethod
	async def to_stdio(self, spec: Dict[str, Any]) -> Dict[str, Any]:
		...
