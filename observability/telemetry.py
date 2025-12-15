"""
Telemetry + metrics for UAAL
"""

from datetime import datetime
from typing import Dict, Any

stats = {
    "actions_total": 0,
    "actions_blocked": 0,
    "approvals_pending": 0,
}

def emit_event(event_type: str, payload: Dict[str, Any]):
    event = {
        "type": event_type,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": payload,
    }
    print("[EVENT]", event)
    stats["actions_total"] += 1
    return event
