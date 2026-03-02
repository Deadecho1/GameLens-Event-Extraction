from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class Span:
    label: str
    start: int  # inclusive
    end: int    # inclusive
    length: int

    def frame_indices(self) -> List[int]:
        if self.end < self.start:
            return []
        return list(range(self.start, self.end + 1))


@dataclass
class ExtractionJob:
    job_id: str
    run_id: str
    label: str
    start: int
    end: int
    length: int

    keyframes: List[int]
    pre_context: List[int]
    post_context: List[int]

    keyframe_paths: List[str]
    pre_context_paths: List[str]
    post_context_paths: List[str]

    params: Dict[str, Any]