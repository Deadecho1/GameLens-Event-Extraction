from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Protocol

from .models import Interval, LinkedInterval
from .timeline import Timeline


class EventPolicy(Protocol):
    def build(
        self,
        interval: Interval,
        timeline: Timeline,
    ) -> Tuple[List[int], List[LinkedInterval], Dict[str, Any]]:
        ...


def _anchors(indices: List[int]) -> List[int]:
    if not indices:
        return []
    if len(indices) == 1:
        return [indices[0]]
    return [indices[0], indices[len(indices) // 2], indices[-1]]


@dataclass(frozen=True)
class ChoicePolicy:
    def build(self, interval: Interval, timeline: Timeline):
        indices = interval.frame_indices()
        keyframes = indices if len(indices) <= 5 else _anchors(indices)
        return keyframes, [], {
            "need_ocr": True,
            "strategy": "choice_sample",
        }


@dataclass(frozen=True)
class EnterLevelPolicy:
    notif_max_after: int = 40

    def build(self, interval: Interval, timeline: Timeline):
        indices = interval.frame_indices()
        keyframes = [indices[0]] if indices else []

        linked: List[LinkedInterval] = []

        ref = timeline.nearest_after(
            frame=interval.end,
            label="notification",
            max_frames=self.notif_max_after,
        )

        if ref is not None:
            n = ref.interval
            linked.append(
                LinkedInterval(
                    role="level_name_notification",
                    label=n.label,
                    start=n.start,
                    end=n.end,
                    length=n.length,
                )
            )

        return keyframes, linked, {
            "strategy": "enter_level_with_notification",
            "need_ocr": True,
            "has_notification": ref is not None,
            "notif_max_after": self.notif_max_after,
        }


@dataclass(frozen=True)
class VictoryPolicy:
    def build(self, interval: Interval, timeline: Timeline):
        indices = interval.frame_indices()
        if not indices:
            return [], [], {}

        if len(indices) == 1:
            keyframes = [indices[0]]
        else:
            keyframes = [indices[len(indices) // 2], indices[-1]]

        return keyframes, [], {
            "need_ocr": True,
            "strategy": "victory_summary",
        }


@dataclass(frozen=True)
class BossFightPolicy:
    sample_every: int = 30
    kill_max_after: int = 120

    def build(self, interval: Interval, timeline: Timeline):
        indices = interval.frame_indices()
        if not indices:
            return [], [], {"valid": False}

        anchors = _anchors(indices)
        periodic = indices[:: self.sample_every]

        seen = set()
        keyframes: List[int] = []
        for i in anchors + periodic:
            if i not in seen:
                seen.add(i)
                keyframes.append(i)

        linked: List[LinkedInterval] = []

        ref = timeline.nearest_after(
            frame=interval.end,
            label="boss-kill",
            max_frames=self.kill_max_after,
        )

        valid = ref is not None

        if ref is not None:
            k = ref.interval
            linked.append(
                LinkedInterval(
                    role="boss_kill_anchor",
                    label=k.label,
                    start=k.start,
                    end=k.end,
                    length=k.length,
                )
            )

        return keyframes, linked, {
            "strategy": "boss_sparse_with_kill_validation",
            "need_healthbar": True,
            "valid": valid,
            "kill_distance_frames": (
                ref.interval.start - interval.end if ref else None
            ),
        }


@dataclass(frozen=True)
class DefaultPolicy:
    def build(self, interval: Interval, timeline: Timeline):
        indices = interval.frame_indices()
        return (indices[:1] if indices else []), [], {"strategy": "default"}


class PolicyRegistry:
    def __init__(self) -> None:
        self._default = DefaultPolicy()
        self._map = {
            "choice": ChoicePolicy(),
            "enter-level": EnterLevelPolicy(),
            "victory": VictoryPolicy(),
            "boss-fight": BossFightPolicy(),
        }

    def get(self, label: str) -> EventPolicy:
        return self._map.get(label, self._default)