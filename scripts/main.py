#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from event_extraction.io_utils import load_spans, write_json
from event_extraction.job_builder import (
    filter_target_spans,
    merge_adjacent_same_label,
    build_jobs,
)
from event_extraction.dispatcher import run_local, run_remote


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spans", required=True, help="Path to JSON spans file")
    ap.add_argument("--images-dir", required=True, help="Directory containing run images indexed by number")
    ap.add_argument("--run-id", required=True, help="Run identifier used for job ids / grouping")
    ap.add_argument("--out", required=True, help="Where to write extraction results JSON")

    ap.add_argument("--mode", choices=["local", "remote"], default="local")
    ap.add_argument("--remote-base-url", default="", help="Base URL for remote worker API (mode=remote)")

    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--merge-gap", type=int, default=0, help="Merge adjacent same-label spans if within this gap")

    args = ap.parse_args()

    spans = load_spans(Path(args.spans))
    spans = filter_target_spans(spans)
    spans = merge_adjacent_same_label(spans, max_gap=args.merge_gap)

    jobs = build_jobs(spans, run_id=args.run_id, images_dir=Path(args.images_dir))

    if args.mode == "remote":
        if not args.remote_base_url:
            raise SystemExit("--remote-base-url is required in remote mode")
        results = run_remote(jobs, base_url=args.remote_base_url, max_workers=args.max_workers)
    else:
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