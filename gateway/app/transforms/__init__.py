from __future__ import annotations
from typing import Callable, Dict
import importlib.util
import pathlib

# Transformer signature: (payload: dict) -> dict
TransformFunc = Callable[[dict], dict]

_registry: Dict[str, TransformFunc] = {}


def register(name: str, func: TransformFunc) -> None:
    _registry[name] = func


def get(name: str) -> TransformFunc | None:
    return _registry.get(name)


def default_passthrough(payload: dict) -> dict:
    return payload


def load_custom_transforms(directory: str) -> None:
    base = pathlib.Path(directory)
    if not base.exists() or not base.is_dir():
        return
    for py_file in base.glob("*.py"):
        module_name = f"gateway.app.transforms.custom.{py_file.stem}"
        spec = importlib.util.spec_from_file_location(module_name, py_file)
        if not spec or not spec.loader:
            continue
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)  # type: ignore[attr-defined]
        except Exception:
            continue
        func = getattr(module, "transform", None)
        if callable(func):
            register(py_file.stem, func)


# register default
register("default", default_passthrough)

# auto-load from default custom dir
load_custom_transforms("gateway/app/transforms/custom")
