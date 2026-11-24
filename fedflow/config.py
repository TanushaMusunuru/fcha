"""Config loading: YAML files with ``extends`` inheritance and ``--set a.b=value`` overrides."""
from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Dict, Iterable

import yaml


def deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    """Recursive merge. A dict in ``override`` containing ``_replace: true`` replaces the base
    dict instead of being merged into it."""
    out = copy.deepcopy(base)
    for key, val in (override or {}).items():
        if isinstance(val, dict) and val.get("_replace"):
            out[key] = {k: copy.deepcopy(v) for k, v in val.items() if k != "_replace"}
        elif isinstance(val, dict) and isinstance(out.get(key), dict):
            out[key] = deep_merge(out[key], val)
        else:
            out[key] = copy.deepcopy(val)
    return out


def load_config(path: str | Path, overrides: Iterable[str] = ()) -> Dict[str, Any]:
    """Load a YAML config. ``extends`` names a parent file or a list of them (relative paths),
    merged in order, with this file's own settings applied last."""
    path = Path(path)
    with open(path, "r", encoding="utf-8") as fh:
        cfg = yaml.safe_load(fh) or {}
    parents = cfg.pop("extends", None)
    if parents:
        merged: Dict[str, Any] = {}
        for parent in [parents] if isinstance(parents, str) else parents:
            merged = deep_merge(merged, load_config(path.parent / parent))
        cfg = deep_merge(merged, cfg)
    for item in overrides:
        set_by_path(cfg, item)
    return cfg


def set_by_path(cfg: Dict[str, Any], assignment: str) -> None:
    """Apply ``a.b.c=value``; the value is parsed as YAML (so numbers, lists and null work)."""
    if "=" not in assignment:
        raise ValueError(f"Override must look like key.path=value, got {assignment!r}")
    key, raw = assignment.split("=", 1)
    node = cfg
    parts = key.strip().split(".")
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    node[parts[-1]] = yaml.safe_load(raw)


def get(cfg: Dict[str, Any], dotted: str, default: Any = None) -> Any:
    node: Any = cfg
    for part in dotted.split("."):
        if not isinstance(node, dict) or part not in node:
            return default
        node = node[part]
    return node
