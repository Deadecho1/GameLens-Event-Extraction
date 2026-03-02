from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple, Protocol

from .models import Span


# ----------------------------
# Policy interface
# ----------------------------

class KeyframePolicy(Protocol):
    def pick(self, span: Span) -> Tuple[List[int], Dict[str, Any]]:
        ...


# ----------------------------
# Helpers
# ----------------------------

def _dedupe_preserve_order(xs: List[int]) -> List[int]:
    seen = set()
    out: List[int] = []
    for x in xs:
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


# ----------------------------
# Concrete policies
# ----------------------------

@dataclass(frozen=True)
class ChoicePolicy:
    """Choice screens are stable: sample a few frames."""
    max_full: int = 5

    def pick(self, span: Span) -> Tuple[List[int], Dict[str, Any]]:
        idxs = span.frame_indices()
        if not idxs:
            return [], {}
        if len(idxs) <= self.max_full:
            k = idxs
        else:
            k = [idxs[0], idxs[len(idxs) // 2], idxs[-1]]
        return k, {"strategy": "choice_sample", "need_ocr": True}


@dataclass(frozen=True)
class TransitionPolicy:
    """Enter/exit level transitions: early frames matter most."""
    extra_offset: int = 2

    def pick(self, span: Span) -> Tuple[List[int], Dict[str, Any]]:
        idxs = span.frame_indices()
        if not idxs:
            return [], {}
        k = [idxs[0]]
        if len(idxs) > self.extra_offset:
            k.append(idxs[self.extra_offset])
        return k, {"strategy": "transition_start", "need_ocr": True}


@dataclass(frozen=True)
class VictoryPolicy:
    """Victory screens: mid + end are usually best summary."""
    def pick(self, span: Span) -> Tuple[List[int], Dict[str, Any]]:
        idxs = span.frame_indices()
        if not idxs:
            return [], {}
        if len(idxs) == 1:
            k = [idxs[0]]
        else:
            k = [idxs[len(idxs) // 2], idxs[-1]]
        return k, {"strategy": "victory_summary", "need_ocr": True}


@dataclass(frozen=True)
class BossFightPolicy:
    """Boss fights can be long: sparse samples + periodic frames."""
    sample_every: int = 30

    def pick(self, span: Span) -> Tuple[List[int], Dict[str, Any]]:
        idxs = span.frame_indices()
        if not idxs:
            return [], {}

        anchors = [idxs[0]]
        if len(idxs) > 1:
            anchors += [idxs[len(idxs) // 2], idxs[-1]]

        periodic = idxs[:: self.sample_every]
        k = _dedupe_preserve_order(anchors + periodic)

        return k, {
            "strategy": "boss_sparse",
            "sample_every": self.sample_every,
            "need_healthbar": True,
            "need_ocr": False,
        }


@dataclass(frozen=True)
class DefaultPolicy:
    """Fallback for unknown labels."""
    def pick(self, span: Span) -> Tuple[List[int], Dict[str, Any]]:
        idxs = span.frame_indices()
        if not idxs:
            return [], {}
        return [idxs[0]], {"strategy": "default"}


# ----------------------------
# Registry
# ----------------------------

class KeyframePicker:
    """
    One place to configure policies.
    Add a new event type by adding a policy + registry entry.
    """

    def __init__(self) -> None:
        self._default: KeyframePolicy = DefaultPolicy()
        self._policies: Dict[str, KeyframePolicy] = {
            "choice": ChoicePolicy(),
            "enter-level": TransitionPolicy(),
            "exit-level": TransitionPolicy(),
            "victory": VictoryPolicy(),
            "boss-fight": BossFightPolicy(sample_every=30),
        }

    def pick(self, span: Span) -> Tuple[List[int], Dict[str, Any]]:
        policy = self._policies.get(span.label, self._default)
        return policy.pick(span)

    def register(self, label: str, policy: KeyframePolicy) -> None:
        self._policies[label] = policy