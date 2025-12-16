
from datetime import datetime

def policy_active(policy):
    active_from = policy.get("active_from")
    if not active_from:
        return True
    return datetime.utcnow() >= datetime.fromisoformat(active_from)
