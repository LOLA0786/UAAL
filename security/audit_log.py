import datetime

AUDIT_LOG = []

def record(event, actor, details):
    AUDIT_LOG.append({
        "event": event,
        "actor": actor,
        "details": details,
        "ts": datetime.datetime.utcnow().isoformat()
    })
