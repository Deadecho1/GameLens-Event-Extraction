from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List

from .models import Span


def _safe_int(x: Any, name: str) -> int:
    if not isinstance(x, int):
        raise ValueError(f"{name} must be int, got {type(x)}")
    return x


def load_spans(path: Path) -> List[Span]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Input JSON must be a list of objects")

    spans: List[Span] = []
    for i, obj in enumerate(raw):
        if not isinstance(obj, dict):
            raise ValueError(f"Item {i} is not an object")

        label = str(obj.get("label", ""))
        start = _safe_int(obj.get("start"), "start")
        end = _safe_int(obj.get("end"), "end")
        length = _safe_int(obj.get("length"), "length")

        spans.append(Span(label=label, start=start, end=end, length=length))

    return spans


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )