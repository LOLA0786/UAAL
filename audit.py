from datetime import datetime

AUDIT_LOG = []

def log_event(api_key: str, action: str):
    AUDIT_LOG.append({
        "time": datetime.utcnow().isoformat(),
        "api_key": api_key,
        "action": action,
    })
