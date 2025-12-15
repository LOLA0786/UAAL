"""
Central approval queue for human-in-the-loop actions.
"""

from typing import Dict, List

# Canonical approval queue
APPROVAL_QUEUE: Dict[str, Dict] = {}

def enqueue(action_id: str, payload: Dict):
    APPROVAL_QUEUE[action_id] = {
        "action_id": action_id,
        "payload": payload,
        "status": "pending",
    }

def approve(action_id: str):
    if action_id in APPROVAL_QUEUE:
        APPROVAL_QUEUE[action_id]["status"] = "approved"

def reject(action_id: str):
    if action_id in APPROVAL_QUEUE:
        APPROVAL_QUEUE[action_id]["status"] = "rejected"

def get(action_id: str):
    return APPROVAL_QUEUE.get(action_id)

def list_pending() -> List[Dict]:
    return [v for v in APPROVAL_QUEUE.values() if v["status"] == "pending"]
