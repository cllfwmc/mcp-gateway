from typing import Dict, Any, List
import time


class MCPRegistry:
	def __init__(self):
		self._items: Dict[str, Dict[str, Any]] = {}

	def list(self) -> List[Dict[str, Any]]:
		return list(self._items.values())

	def upsert(self, key: str, data: Dict[str, Any]):
		data["updated_at"] = int(time.time())
		self._items[key] = data

	def get(self, key: str) -> Dict[str, Any] | None:
		return self._items.get(key)

	def heartbeat(self, key: str):
		if key in self._items:
			self._items[key]["last_heartbeat"] = int(time.time())
