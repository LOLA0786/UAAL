from db import get_db
import json

def init_db():
    with get_db() as db:
        db.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            api_key TEXT PRIMARY KEY,
            owner TEXT,
            role TEXT,
            scopes TEXT,
            policy TEXT
        )
        """)

        db.execute("""
        CREATE TABLE IF NOT EXISTS audit_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_key TEXT,
            action TEXT,
            decision TEXT,
            reason TEXT,
            message TEXT,
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

def log_audit(api_key, action, decision, reason=None, message=None):
    with get_db() as db:
        db.execute(
            """
            INSERT INTO audit_events (api_key, action, decision, reason, message)
            VALUES (?, ?, ?, ?, ?)
            """,
            (api_key, action, decision, reason, message)
        )

def log_audit_v2(
    api_key,
    action,
    decision,
    reason=None,
    message=None,
    agent_owner=None,
    agent_role=None,
    scopes=None,
    policy=None,
    risk_level="LOW",
    latency_ms=None
):
    with get_db() as db:
        db.execute(
            """
            INSERT INTO audit_events
            (api_key, action, decision, reason, message, ts)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (api_key, action, decision, reason, message)
        )

def classify_risk(reason):
    if reason == "UNKNOWN_AGENT":
        return "HIGH"
    if reason in ("SCOPE_DENIED", "POLICY_TIME_DENIED"):
        return "MEDIUM"
    return "LOW"

def log_audit_v2(
    api_key,
    action,
    decision,
    reason=None,
    message=None,
    agent_owner=None,
    scopes=None,
    policy=None,
    latency_ms=None
):
    risk = classify_risk(reason)

    with get_db() as db:
        db.execute(
            """
            INSERT INTO audit_events
            (api_key, action, decision, reason, message, ts)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """,
            (api_key, action, decision, reason, message)
        )

    return risk
