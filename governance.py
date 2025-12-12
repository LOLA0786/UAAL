from db import SessionLocal, AuditLog, User
import datetime
import random
import string

# Simulate a 2FA code store (in memory for demo). For production use OTP services
TWO_FA = {}  # user_id -> (code, expiry_ts)

def generate_2fa(user_id, ttl=300):
    code = ''.join(random.choices(string.digits, k=6))
    expiry = int(datetime.datetime.utcnow().timestamp()) + ttl
    TWO_FA[user_id] = (code, expiry)
    return code

def verify_2fa(user_id, code):
    rec = TWO_FA.get(user_id)
    if not rec:
        return False
    saved_code, expiry = rec
    if int(datetime.datetime.utcnow().timestamp()) > expiry:
        TWO_FA.pop(user_id, None)
        return False
    if saved_code == code:
        TWO_FA.pop(user_id, None)
        return True
    return False

def is_high_risk(action):
    # heuristic: verbs that include payment/transfer/delete or object_type payment
    v = (action.get("verb") or "").lower()
    objt = (action.get("object",{}).get("type") or "").lower()
    risky = any(k in v for k in ("pay", "transfer", "charge", "delete", "remove")) or "payment" in objt
    return risky

def enforce_spend_limit(action, user_id):
    # wrapper to call policy.check_spending_limits style logic; simplified
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or user.spending_limit <= 0:
            return True, "no limit"
        cost = float(action.get("parameters",{}).get("cost", 0.0))
        # compute month total
        first = datetime.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        rows = db.query(ActionRecord).filter(ActionRecord.actor_id==user_id, ActionRecord.timestamp >= first).all()
        total = sum(float((r.parameters or {}).get("cost", 0.0) or 0.0) for r in rows)
        if (total + cost) > user.spending_limit:
            return False, f"exceeded limit {total + cost} > {user.spending_limit}"
        return True, "ok"
    finally:
        db.close()
