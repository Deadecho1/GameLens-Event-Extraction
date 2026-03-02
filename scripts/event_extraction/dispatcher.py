from __future__ import annotations

from dataclasses import asdict
from typing import Any, Dict, List
from concurrent.futures import ThreadPoolExecutor, as_completed

from .models import ExtractionJob
from .workers.local_workers import LOCAL_WORKERS
from .workers.remote_client import post_json, REMOTE_ENDPOINTS

def run_local(jobs: List[ExtractionJob], max_workers: int) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = []
        for job in jobs:
            fn = LOCAL_WORKERS.get(job.label)
            if fn is None:
                continue
            futs.append(ex.submit(fn, job))

        for fut in as_completed(futs):
            results.append(fut.result())

    return results


def run_remote(jobs: List[ExtractionJob], base_url: str, max_workers: int) -> List[Dict[str, Any]]:
    base_url = base_url.rstrip("/")
    results: List[Dict[str, Any]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        futs = []
        for job in jobs:
            suffix = REMOTE_ENDPOINTS.get(job.label)
            if not suffix:
                continue
            url = f"{base_url}{suffix}"
            payload = asdict(job)
            futs.append(ex.submit(post_json, url, payload))

        for fut in as_completed(futs):
            results.append(fut.result())

    return results