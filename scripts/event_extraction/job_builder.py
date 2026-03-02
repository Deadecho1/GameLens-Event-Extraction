from __future__ import annotations
from pathlib import Path
from typing import List

from .models import Interval, ExtractionJob
from .timeline import Timeline
from .policies import PolicyRegistry


TARGET_LABELS = {
    "choice",
    "enter-level",
    "victory",
    "boss-fight",
}


def resolve_frame_path(images_dir: Path, idx: int) -> str:
    candidates = [
        images_dir / f"{idx}.jpg",
        images_dir / f"{idx}.png",
        images_dir / f"{idx:06d}.jpg",
        images_dir / f"{idx:06d}.png",
    ]
    for p in candidates:
        if p.exists():
            return str(p.resolve())
    return str((images_dir / f"{idx}.jpg").resolve())


def build_jobs(
    all_intervals: List[Interval],
    run_id: str,
    images_dir: Path,
) -> List[ExtractionJob]:

    timeline = Timeline(all_intervals)
    registry = PolicyRegistry()

    targets = [
        i for i in all_intervals
        if i.label in TARGET_LABELS
    ]

    targets = sorted(targets, key=lambda i: (i.start, i.end))

    jobs: List[ExtractionJob] = []

    for n, interval in enumerate(targets):

        policy = registry.get(interval.label)
        keyframes, linked, params = policy.build(interval, timeline)

        job_id = f"{run_id}:{interval.label}:{interval.start}-{interval.end}:{n}"

        jobs.append(
            ExtractionJob(
                job_id=job_id,
                run_id=run_id,
                label=interval.label,
                start=interval.start,
                end=interval.end,
                length=interval.length,
                keyframes=keyframes,
                keyframe_paths=[
                    resolve_frame_path(images_dir, k)
                    for k in keyframes
                ],
                linked=linked,
                params=params,
            )
        )

    return jobs