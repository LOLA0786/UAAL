import sqlite3
from pathlib import Path

DB_PATH = Path("uaal.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trace_id TEXT,
        org TEXT,
        agent TEXT,
        action TEXT,
        status TEXT,
        reason TEXT,
        timestamp TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS approvals (
        trace_id TEXT PRIMARY KEY,
        expires_at TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

def record_approval(trace_id, approver_role):
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    UPDATE approvals
    SET status='approved'
    WHERE trace_id=?
    """, (trace_id,))

    conn.commit()
    conn.close()

def init_approval(trace_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    INSERT OR IGNORE INTO approvals
    (trace_id, finance, security)
    VALUES (?, 0, 0)
    """, (trace_id,))
    conn.commit()
    conn.close()

def approve(trace_id, role):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"""
    UPDATE approvals
    SET {role}=1
    WHERE trace_id=?
    """, (trace_id,))
    conn.commit()
    conn.close()

def fully_approved(trace_id) -> bool:
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
    SELECT finance, security FROM approvals WHERE trace_id=?
    """, (trace_id,))
    row = cur.fetchone()
    conn.close()
    return row and row["finance"] == 1 and row["security"] == 1
