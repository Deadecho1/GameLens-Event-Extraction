from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from .models import Interval, ExtractionJob
from .keyframes import KeyframePicker


TARGET_LABELS = {
    "choice",
    "enter-level",
    "exit-level",
    "victory",
    "boss-fight",
}


def filter_target_intervals(intervals: List[Interval]) -> List[Interval]:
    return [s for s in intervals if s.label in TARGET_LABELS]


def add_context(
    interval: Interval,
    pre: int,
    post: int,
    min_idx: int = 0,
    max_idx: Optional[int] = None,
) -> Tuple[List[int], List[int]]:
    pre_idxs: List[int] = []
    post_idxs: List[int] = []

    for i in range(pre):
        j = interval.start - (pre - i)
        if j >= min_idx and (max_idx is None or j <= max_idx):
            pre_idxs.append(j)

    for i in range(post):
        j = interval.end + 1 + i
        if j >= min_idx and (max_idx is None or j <= max_idx):
            post_idxs.append(j)

    return pre_idxs, post_idxs


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


def build_jobs(spans: List[Interval], run_id: str, images_dir: Path) -> List[ExtractionJob]:
    jobs: List[ExtractionJob] = []

    picker = KeyframePicker()
    for n, s in enumerate(spans):
        keyframes, params = picker.pick(s)

        if s.label in ("enter-level", "exit-level"):
            pre, post = 2, 2
        elif s.label == "boss-fight":
            pre, post = 1, 1
        else:
            pre, post = 1, 1

        pre_ctx, post_ctx = add_context(s, pre=pre, post=post)

        job_id = f"{run_id}:{s.label}:{s.start}-{s.end}:{n}"

        jobs.append(
            ExtractionJob(
                job_id=job_id,
                run_id=run_id,
                label=s.label,
                start=s.start,
                end=s.end,
                length=s.length,
                keyframes=keyframes,
                pre_context=pre_ctx,
                post_context=post_ctx,
                keyframe_paths=[resolve_frame_path(images_dir, i) for i in keyframes],
                pre_context_paths=[resolve_frame_path(images_dir, i) for i in pre_ctx],
                post_context_paths=[resolve_frame_path(images_dir, i) for i in post_ctx],
                params=params,
            )
        )

    return jobs