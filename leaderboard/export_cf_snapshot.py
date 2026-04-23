#!/usr/bin/env python3
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError, HTTPError
from urllib.request import urlopen


def main() -> int:
    api_url = os.environ.get("LEADERBOARD_API_URL", "http://localhost:80/api/leaderboard")
    out_dir = Path(os.environ.get("CF_STATIC_DIR", Path(__file__).resolve().parent / "cf-static"))
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        with urlopen(api_url, timeout=10) as resp:
            payload = json.load(resp)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
        print(f"[ERROR] Failed to fetch leaderboard from {api_url}: {exc}")
        return 1

    snapshot = {
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "source": api_url,
        "user": payload.get("user", []),
        "root": payload.get("root", []),
    }

    out_file = out_dir / "leaderboard.json"
    out_file.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] Snapshot exported: {out_file}")
    print(f"[OK] User records: {len(snapshot['user'])}, Root records: {len(snapshot['root'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
