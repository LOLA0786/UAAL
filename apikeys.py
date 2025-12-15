import secrets
import sqlite3
from typing import Optional, Dict

DB_PATH = "uaal_v2.db"

def _conn():
    return sqlite3.connect(DB_PATH)


def init_api_keys():
    with _conn() as c:
        c.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            key TEXT PRIMARY KEY,
            owner TEXT,
            role TEXT,
            active INTEGER DEFAULT 1
        )
        """)
        c.commit()


def create_api_key(owner: str, role: str = "agent") -> str:
    init_api_keys()
    key = secrets.token_urlsafe(32)

    with _conn() as c:
        c.execute(
            "INSERT INTO api_keys (key, owner, role) VALUES (?, ?, ?)",
            (key, owner, role),
        )
        c.commit()

    return key


def verify_api_key(key: str) -> Optional[Dict]:
    init_api_keys()

    with _conn() as c:
        row = c.execute(
            "SELECT key, owner, role FROM api_keys WHERE key = ? AND active = 1",
            (key,),
        ).fetchone()

    if not row:
        return None

    return {
        "key": row[0],
        "owner": row[1],
        "role": row[2],
    }
