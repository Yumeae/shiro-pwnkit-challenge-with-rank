#!/usr/bin/env python3
"""Fetch current leaderboard JSON once and save it for static hosting."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

DEFAULT_SOURCE = "http://39.106.85.149/api/leaderboard"
DEFAULT_OUTPUT = "cf-static/leaderboard.json"


def normalize_rows(rows: Any) -> list[dict[str, Any]]:
    if not isinstance(rows, list):
        return []

    normalized: list[dict[str, Any]] = []
    for idx, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            continue
        name = str(row.get("name", "")).strip()
        if not name:
            continue
        normalized.append(
            {
                "rank": int(row.get("rank") or idx),
                "name": name,
                "time": str(row.get("time", "")),
            }
        )
    return normalized


def fetch_json(url: str, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (LeaderboardSnapshot/1.0)",
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("Invalid leaderboard payload: top-level JSON must be object")
    return {
        "user": normalize_rows(data.get("user", [])),
        "root": normalize_rows(data.get("root", [])),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Export leaderboard snapshot for static hosting")
    parser.add_argument("--source", default=DEFAULT_SOURCE, help="Leaderboard API URL")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Snapshot JSON output path")
    parser.add_argument("--timeout", type=int, default=20, help="HTTP timeout in seconds")
    args = parser.parse_args()

    try:
        snapshot = fetch_json(args.source, args.timeout)
    except (urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        print(f"[ERROR] failed to fetch snapshot: {exc}", file=sys.stderr)
        return 1

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"[OK] snapshot saved: {out}")
    print(f"      user: {len(snapshot['user'])}, root: {len(snapshot['root'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
