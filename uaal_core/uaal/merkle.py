import os, json, hashlib
from datetime import date

BASE_DIR = os.getcwd()
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")
ROOTS_DIR = os.path.join(EVIDENCE_DIR, "roots")
os.makedirs(ROOTS_DIR, exist_ok=True)

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def compute_daily_root(day=None):
    day = day or date.today().isoformat()
    hashes = []

    if not os.path.exists(EVIDENCE_DIR):
        return None

    for f in sorted(os.listdir(EVIDENCE_DIR)):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(EVIDENCE_DIR, f), "rb") as fh:
            hashes.append(sha256(fh.read()))

    if not hashes:
        return None

    while len(hashes) > 1:
        if len(hashes) % 2 == 1:
            hashes.append(hashes[-1])
        hashes = [
            sha256((hashes[i] + hashes[i+1]).encode())
            for i in range(0, len(hashes), 2)
        ]

    root = hashes[0]
    out = {"date": day, "root": root, "count": len(hashes)}

    with open(os.path.join(ROOTS_DIR, f"{day}.json"), "w") as f:
        json.dump(out, f, indent=2)

    return out
