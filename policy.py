from datetime import datetime, timedelta

SLA_SECONDS = 20  # demo-friendly

def approval_expired(requested_at: str) -> bool:
    ts = datetime.fromisoformat(requested_at)
    return datetime.utcnow() > ts + timedelta(seconds=SLA_SECONDS)
