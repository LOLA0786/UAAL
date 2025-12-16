import sqlite3
from contextlib import contextmanager

DB_PATH = "uaal.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Agents table
    c.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        api_key TEXT PRIMARY KEY,
        owner TEXT,
        role TEXT,
        scopes TEXT,
        policy TEXT
    )
    """)

    # Audit log table
    c.execute("""
    CREATE TABLE IF NOT EXISTS audit_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        api_key TEXT,
        action TEXT,
        decision TEXT,
        reason TEXT,
        message TEXT,
        ts TEXT
    )
    """)

    conn.commit()
    conn.close()

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
