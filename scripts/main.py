#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from event_extraction.io_utils import load_intervals, write_json
from event_extraction.job_builder import build_jobs
from event_extraction.dispatcher import run_local


def main() -> int:
    ap = argparse.ArgumentParser()

    ap.add_argument("--intervals", required=True, help="Path to JSON intervals file")
    ap.add_argument("--images-dir", required=True, help="Directory containing run images indexed by number")
    ap.add_argument("--run-id", required=True, help="Run identifier used for job ids / grouping")
    ap.add_argument("--out", required=True, help="Where to write extraction results JSON")

    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--merge-gap", type=int, default=0, help="Merge adjacent same-label intervals if within this gap")

    args = ap.parse_args()

    intervals = load_intervals(Path(args.intervals))

    # build_jobs now expects *all* intervals (including notification/boss-kill)
    # so policies can link nearby events.
    jobs = build_jobs(
        all_intervals=intervals,
        run_id=args.run_id,
        images_dir=Path(args.images_dir),
        merge_gap=args.merge_gap,
    )

    results = run_local(jobs, max_workers=args.max_workers)

    write_json(
        Path(args.out),
        {
            "run_id": args.run_id,
            "job_count": len(jobs),
            "results": results,
        },
    )

    print(f"Wrote {len(results)} results to: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())