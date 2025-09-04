from typing import Dict, Any, Callable

from ..adapters.standard import StandardMCPAdapter
from ..adapters.custom import CustomMCPAdapter


class ConversionService:
	def __init__(self):
		self._standard = StandardMCPAdapter()

	async def convert(self, source: Dict[str, Any], target: str, custom_script: str | None) -> Dict[str, Any]:
		if custom_script:
			def transformer(spec: Dict[str, Any], t: str) -> Dict[str, Any]:
				# WARNING: Placeholder. In production, sandbox execution.
				local_vars: Dict[str, Any] = {}
				exec(custom_script, {"__builtins__": {}}, local_vars)
				func: Callable[[Dict[str, Any], str], Dict[str, Any]] = local_vars.get("transform")
				if not func:
					raise ValueError("Custom script must define transform(spec, target)")
				return func(spec, t)

			adapter = CustomMCPAdapter(transformer)
		else:
			adapter = self._standard

		if target == "streamable-http":
			return await adapter.to_streamable_http(source)
		if target == "sse":
			return await adapter.to_sse(source)
		if target == "stdio":
			return await adapter.to_stdio(source)
		raise ValueError("Unsupported target protocol")
