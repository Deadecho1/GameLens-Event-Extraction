from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional, Iterable
from .models import Interval


@dataclass(frozen=True)
class IntervalRef:
    idx: int
    interval: Interval


class Timeline:
    def __init__(self, intervals: List[Interval]) -> None:
        self.intervals: List[Interval] = sorted(
            intervals, key=lambda i: (i.start, i.end)
        )

    def iter_after(self, frame: int) -> Iterable[IntervalRef]:
        for i, interval in enumerate(self.intervals):
            if interval.start > frame:
                yield IntervalRef(i, interval)

    def iter_before(self, frame: int) -> Iterable[IntervalRef]:
        for i in range(len(self.intervals) - 1, -1, -1):
            interval = self.intervals[i]
            if interval.end < frame:
                yield IntervalRef(i, interval)

    def nearest_after(
        self,
        frame: int,
        label: str,
        max_frames: int,
    ) -> Optional[IntervalRef]:

        for ref in self.iter_after(frame):
            if ref.interval.label != label:
                continue
            if ref.interval.start - frame <= max_frames:
                return ref
            return None
        return None

    def nearest_before(
        self,
        frame: int,
        label: str,
        max_frames: int,
    ) -> Optional[IntervalRef]:

        for ref in self.iter_before(frame):
            if ref.interval.label != label:
                continue
            if frame - ref.interval.end <= max_frames:
                return ref
            return None
        return None