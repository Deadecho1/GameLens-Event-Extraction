from __future__ import annotations

import json
from dataclasses import asdict
from typing import Any, Dict, List
from urllib.request import Request, urlopen

from ..models import ExtractionJob


REMOTE_ENDPOINTS: Dict[str, str] = {
    "choice": "/extract/choice",
    "enter-level": "/extract/transition",
    "exit-level": "/extract/transition",
    "victory": "/extract/victory",
    "boss-fight": "/extract/boss_fight",
}


def post_json(url: str, payload: Dict[str, Any], timeout_s: float = 30.0) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=timeout_s) as resp:
        body = resp.read().decode("utf-8")
        return json.loads(body) if body else {"ok": True}


def dispatch_remote(jobs: List[ExtractionJob], base_url: str) -> List[Dict[str, Any]]:
    base_url = base_url.rstrip("/")
    results: List[Dict[str, Any]] = []

    for job in jobs:
        suffix = REMOTE_ENDPOINTS.get(job.label)
        if not suffix:
            continue
        url = f"{base_url}{suffix}"
        results.append(post_json(url, asdict(job)))

    return results