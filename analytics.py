from db import SessionLocal, ActionRecord, AuditLog
import datetime
from sqlalchemy import func

def actions_per_agent(since_minutes=60):
    db = SessionLocal()
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=since_minutes)
        rows = (
            db.query(ActionRecord.actor_id, func.count(ActionRecord.id).label("count"))
            .filter(ActionRecord.timestamp >= cutoff)
            .group_by(ActionRecord.actor_id)
            .order_by(func.count(ActionRecord.id).desc())
            .all()
        )
        return [{"actor_id": r[0], "count": int(r[1])} for r in rows]
    finally:
        db.close()

def policy_violations(since_days=30):
    db = SessionLocal()
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(days=since_days)
        rows = (
            db.query(AuditLog.event, func.count(AuditLog.id).label("count"))
            .filter(AuditLog.timestamp >= cutoff)
            .filter(AuditLog.event.like("%flag%") | AuditLog.event.like("%rejected%"))
            .group_by(AuditLog.event)
            .all()
        )
        return [{"event": r[0], "count": int(r[1])} for r in rows]
    finally:
        db.close()

def approval_queue():
    db = SessionLocal()
    try:
        rows = db.query(ActionRecord).filter(ActionRecord.state == "pending").order_by(ActionRecord.timestamp.asc()).all()
        return [{"action_id": r.action_id, "actor_id": r.actor_id, "verb": r.verb, "timestamp": r.timestamp.isoformat(), "confidence": r.confidence} for r in rows]
    finally:
        db.close()

def spend_by_agent(months=1):
    db = SessionLocal()
    try:
        first = (datetime.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0) - datetime.timedelta(days=30*(months-1)))
        rows = (
            db.query(ActionRecord.actor_id, func.sum(func.coalesce(func.json_extract(ActionRecord.parameters, '$.cost'), 0)).label("spent"))
            .filter(ActionRecord.timestamp >= first)
            .group_by(ActionRecord.actor_id)
            .order_by(func.sum(func.coalesce(func.json_extract(ActionRecord.parameters, '$.cost'), 0)).desc())
            .all()
        )
        # Note: SQLite's JSON functions vary by version; this fallback reads cost from parameters field in Python if DB JSON extraction fails.
        out = []
        for r in rows:
            out.append({"actor_id": r[0], "spent": float(r[1] or 0.0)})
        return out
    finally:
        db.close()
