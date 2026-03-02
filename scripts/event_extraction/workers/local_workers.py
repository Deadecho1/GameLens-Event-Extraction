from __future__ import annotations

from typing import Any, Dict, Callable

from ..models import ExtractionJob


def extract_choice(job: ExtractionJob) -> Dict[str, Any]:
    # TODO: implement:
    # - OCR on choice panel
    # - detect options + which was selected
    return {"job_id": job.job_id, "label": job.label, "extracted": {"todo": "choice"}}


def extract_transition(job: ExtractionJob) -> Dict[str, Any]:
    # TODO: implement:
    # - determine biome/room type
    # - enter vs exit level if you start emitting "exit-level"
    return {"job_id": job.job_id, "label": job.label, "extracted": {"todo": "transition"}}


def extract_victory(job: ExtractionJob) -> Dict[str, Any]:
    # TODO: implement:
    # - parse victory stats screen
    return {"job_id": job.job_id, "label": job.label, "extracted": {"todo": "victory"}}


def extract_boss_fight(job: ExtractionJob) -> Dict[str, Any]:
    # TODO: implement:
    # - detect boss identity via HP bar region / icon
    # - detect phases, etc.
    return {"job_id": job.job_id, "label": job.label, "extracted": {"todo": "boss-fight"}}


LOCAL_WORKERS: Dict[str, Callable[[ExtractionJob], Dict[str, Any]]] = {
    "choice": extract_choice,
    "enter-level": extract_transition,
    "exit-level": extract_transition,
    "victory": extract_victory,
    "boss-fight": extract_boss_fight,
}