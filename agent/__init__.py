"""Public package surface.

`root_agent` is lazy: it is constructed on first access (see `agent.agent.__getattr__`).
Importing this package does not require a MongoDB connection string.
"""

from __future__ import annotations

from typing import Any

__all__ = ["root_agent"]


def __getattr__(name: str) -> Any:
    if name == "root_agent":
        from . import agent as _agent

        value = _agent.root_agent
        globals()["root_agent"] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
