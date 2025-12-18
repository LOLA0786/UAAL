import os
import json
from datetime import date
from uaal.merkle import compute_daily_root

BASE_DIR = os.getcwd()
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")
ROOTS_DIR = os.path.join(EVIDENCE_DIR, "roots")


def verify_day(day=None):
    day = day or date.today().isoformat()
    root_file = os.path.join(ROOTS_DIR, f"{day}.json")

    if not os.path.exists(root_file):
        raise RuntimeError(f"No stored root for {day}")

    with open(root_file) as f:
        stored = json.load(f)

    recomputed = compute_daily_root(day)

    if recomputed is None:
        raise RuntimeError("No evidence to verify")

    ok = stored["root"] == recomputed["root"]

    return {
        "date": day,
        "status": "OK" if ok else "TAMPERED",
        "stored_root": stored["root"],
        "computed_root": recomputed["root"],
        "count": stored.get("count"),
    }
