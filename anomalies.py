from db import SessionLocal, ActionRecord
import datetime
import statistics

# simple anomaly detectors

def low_confidence_alert(threshold=0.5, lookback_minutes=60):
    db = SessionLocal()
    try:
        cutoff = datetime.datetime.utcnow() - datetime.timedelta(minutes=lookback_minutes)
        rows = db.query(ActionRecord).filter(ActionRecord.timestamp >= cutoff).all()
        alerts = []
        for r in rows:
            if (r.confidence or 0.0) < threshold:
                alerts.append({"action_id": r.action_id, "actor_id": r.actor_id, "confidence": r.confidence})
        return alerts
    finally:
        db.close()

def zscore_confidence_anomalies(lookback=500, z_threshold=3.0):
    db = SessionLocal()
    try:
        rows = db.query(ActionRecord).order_by(ActionRecord.timestamp.desc()).limit(lookback).all()
        vals = [float(r.confidence or 0.0) for r in rows]
        if len(vals) < 10:
            return []
        mean = statistics.mean(vals)
        stdev = statistics.pstdev(vals) or 1e-6
        anomalies = []
        for r in rows:
            z = (float(r.confidence or 0.0) - mean) / stdev
            if abs(z) > z_threshold:
                anomalies.append({"action_id": r.action_id, "actor_id": r.actor_id, "confidence": r.confidence, "z": z})
        return anomalies
    finally:
        db.close()
