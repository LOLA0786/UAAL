import json
import os
import uuid
from datetime import datetime
from uaal.merkle import compute_daily_root

BASE_DIR = os.getcwd()
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")
os.makedirs(EVIDENCE_DIR, exist_ok=True)


def emit_evidence(decision):
    """
    Write evidence as immutable JSON and update daily Merkle root.
    """

    record = {
        "id": decision.id,
        "agent": decision.agent,
        "action": decision.action,
        "payload": decision.payload,
        "allowed": decision.allowed,
        "reason": decision.reason,
        "policy": decision.policy,
        "timestamp": decision.timestamp,
        "written_at": datetime.utcnow().isoformat(),
    }

    fname = f"{record['timestamp']}_{decision.id}.json"
    path = os.path.join(EVIDENCE_DIR, fname)

    # 1. Write immutable evidence
    with open(path, "w") as f:
        json.dump(record, f, indent=2)

    # 2. Update Merkle root (daily)
    compute_daily_root()

    return path
