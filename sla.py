import threading
import time
from datetime import datetime
from storage import get_db
from config import SLA_CHECK_INTERVAL_SEC

def sla_worker():
    while True:
        conn = get_db()
        cur = conn.cursor()

        now = datetime.utcnow().isoformat()
        cur.execute("""
        UPDATE approvals
        SET status='rejected'
        WHERE expires_at < ? AND status='pending'
        """, (now,))

        conn.commit()
        conn.close()
        time.sleep(SLA_CHECK_INTERVAL_SEC)

def start_sla_worker():
    t = threading.Thread(target=sla_worker, daemon=True)
    t.start()
