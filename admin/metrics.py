from storage import get_db

def metrics():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM audit")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit WHERE status='approved'")
    approved = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit WHERE status='rejected'")
    rejected = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM audit WHERE status='needs_approval'")
    pending = cur.fetchone()[0]

    conn.close()

    return {
        "total_actions": total,
        "approved": approved,
        "rejected": rejected,
        "pending": pending
    }
