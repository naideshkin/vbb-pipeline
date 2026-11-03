"""
Step 0 — explore the VBB departures API.

Usage:
    pip install requests pandas
    python explore_departures.py fetch            # save one snapshot per stop
    python explore_departures.py analyze          # run the checks on saved snapshots

Fetching and saving are done for you. Every function marked TODO is yours to write.
"""

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://v6.vbb.transport.rest"
SAMPLES_DIR = Path("docs/samples")

# TODO: replace with your chosen stops (find IDs via /locations?query=...)
STOPS = {
    "900100003": "S+U Alexanderplatz",
    "900054105": "S+U Innsbrucker Platz (Berlin)",
    "900023201": "S+U Zoologischer Garten Bhf (Berlin)",
}

DURATION_MIN = 30


# ---------------------------------------------------------------------------
# Fetching (done)
# ---------------------------------------------------------------------------


def fetch_departures(stop_id: str, duration: int = DURATION_MIN) -> dict:
    """Call /stops/{id}/departures and return the parsed JSON."""
    resp = requests.get(
        f"{BASE_URL}/stops/{stop_id}/departures",
        params={"duration": duration},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()


def save_snapshot(stop_id: str, data: dict) -> Path:
    """Save raw response as docs/samples/<stop_id>_<UTC timestamp>.json."""
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = SAMPLES_DIR / f"{stop_id}_{ts}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_snapshot(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def get_path(record: dict, dotted: str):
    """Read a nested value, e.g. get_path(dep, "line.id"). Returns None if missing."""
    value = record
    for part in dotted.split("."):
        if not isinstance(value, dict):
            return None
        value = value.get(part)
    return value


# ---------------------------------------------------------------------------
# Your analysis (TODO)
# ---------------------------------------------------------------------------


def inspect_structure(data: dict) -> None:
    # 1. What's at the top level of the response?
    print("Top-level keys:", list(data.keys()))

    # 2. How many departures did we get?
    departures = data["departures"]
    print("Number of departures:", len(departures))
    if not departures:
        return  # nothing more to inspect

    # 3. What fields does one departure have, and what type is each?
    first = departures[0]
    print("\nFields of one departure:")
    for key, value in first.items():
        print(f"  {key}: {type(value).__name__}")

    # 4. Which fields are nested objects, and what's inside them?
    for key, value in first.items():
        if isinstance(value, dict):
            print(f"\nNested '{key}' has keys: {list(value.keys())}")


def check_unique_key(records: list[dict], key_fields: list[str]) -> bool:
    from collections import Counter

    # 1. one key tuple per record
    keys = [tuple(get_path(record, f) for f in key_fields) for record in records]

    # 2. count how often each key appears
    counts = Counter(keys)

    # 3. keep only the keys that appear more than once
    duplicates = {k: n for k, n in counts.items() if n > 1}

    print(f"\nKey {key_fields}: {len(keys)} records, {len(counts)} distinct keys")
    if duplicates:
        print(f"{len(duplicates)} duplicated keys, e.g.:")
        for k, n in list(duplicates.items())[:5]:
            print(f"  {k} appears {n} times")
        return False

    print("Key is unique")
    return True


def compare_snapshots(
    older: list[dict], newer: list[dict], key_fields: list[str]
) -> None:
    """
    Q3 — Same departure across polls.
    TODO:
      - index both lists by key
      - keys only in `older`  -> why did they disappear?
      - keys only in `newer`  -> why did they appear?
      - keys in both          -> print which fields changed, with old -> new values
    Hint: compare flattened records (pd.json_normalize) so nested changes show up too.
    """
    raise NotImplementedError


def profile_fields(records: list[dict]) -> None:
    """
    Q4 — Nested and nullable fields.
    TODO:
      - df = pd.json_normalize(records)
      - null count / share per column
      - columns that are lists (e.g. remarks) — json_normalize won't flatten those
      - do all records have the same set of keys?
    """
    raise NotImplementedError


# ---------------------------------------------------------------------------
# CLI (done)
# ---------------------------------------------------------------------------


def cmd_fetch() -> None:
    for stop_id, name in STOPS.items():
        data = fetch_departures(stop_id)
        path = save_snapshot(stop_id, data)
        print(f"{name}: {len(data.get('departures', []))} departures -> {path}")
        time.sleep(1)  # be polite to the shared API (100 req/min limit)


def cmd_analyze() -> None:
    files = sorted(SAMPLES_DIR.glob("*.json"))
    if not files:
        print("No snapshots yet — run `fetch` first.")
        return

    snapshots = {f: load_snapshot(f) for f in files}

    # Q1
    inspect_structure(next(iter(snapshots.values())))

    # Q2 — TODO: put your candidate key here
    key_fields = ["tripId"]
    all_records = [dep for data in snapshots.values() for dep in data["departures"]]
    check_unique_key(all_records, key_fields)

    # Q3 — compare the two oldest snapshots of the same stop
    by_stop: dict[str, list[Path]] = {}
    for f in files:
        by_stop.setdefault(f.stem.split("_")[0], []).append(f)
    for stop_id, stop_files in by_stop.items():
        if len(stop_files) >= 2:
            print(
                f"\n=== {STOPS.get(stop_id, stop_id)}: {stop_files[0].name} vs {stop_files[1].name}"
            )
            compare_snapshots(
                snapshots[stop_files[0]]["departures"],
                snapshots[stop_files[1]]["departures"],
                key_fields,
            )

    # Q4
    profile_fields(all_records)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["fetch", "analyze"])
    args = parser.parse_args()
    cmd_fetch() if args.command == "fetch" else cmd_analyze()
