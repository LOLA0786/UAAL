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
            ts DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
