import csv
from fastapi.responses import StreamingResponse
from storage import get_db

def export_audit_csv():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM audit")
    rows = cur.fetchall()

    def stream():
        writer = csv.writer(iter([]))
        header = rows[0].keys() if rows else []
        yield ",".join(header) + "\n"
        for r in rows:
            yield ",".join(str(v) for v in r) + "\n"

    return StreamingResponse(stream(), media_type="text/csv")
