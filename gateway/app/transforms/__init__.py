from __future__ import annotations
from typing import Callable, Dict, Any

# Transformer signature: (payload: dict) -> dict
TransformFunc = Callable[[dict], dict]

_registry: Dict[str, TransformFunc] = {}


def register(name: str, func: TransformFunc) -> None:
    _registry[name] = func


def get(name: str) -> TransformFunc | None:
    return _registry.get(name)


def default_passthrough(payload: dict) -> dict:
    return payload

# register default
register("default", default_passthrough)
