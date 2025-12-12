from db import SessionLocal, ActionRecord, AuditLog, User, Watchlist
import datetime

DEFAULT_CONFIDENCE_THRESHOLD = 0.6
DEFAULT_RATE_LIMIT_PER_MIN = 10  # actions per minute per actor considered anomalous

def log_audit(action_id, user, event, details):
    db = SessionLocal()
    try:
        a = AuditLog(action_id=action_id, user=user, event=event, details=details)
        db.add(a)
        db.commit()
    finally:
        db.close()

def check_watchlists(action):
    db = SessionLocal()
    try:
        wls = db.query(Watchlist).all()
        for w in wls:
            if w.field == "verb" and action.get("verb") == w.value:
                if w.type == "blacklist":
                    return False, f"verb {w.value} is blacklisted"
                if w.type == "whitelist":
                    return True, f"verb {w.value} is whitelisted"
            if w.field == "actor_id" and action.get("actor",{}).get("id") == w.value:
                if w.type == "blacklist":
                    return False, f"actor {w.value} is blacklisted"
                if w.type == "whitelist":
                    return True, f"actor {w.value} is whitelisted"
            if w.field == "object_type" and action.get("object",{}).get("type") == w.value:
                if w.type == "blacklist":
                    return False, f"object_type {w.value} is blacklisted"
                if w.type == "whitelist":
                    return True, f"object_type {w.value} is whitelisted"
        return None, "no explicit watchlist rule"
    finally:
        db.close()

def rate_check(action):
    db = SessionLocal()
    try:
        actor = action.get("actor",{}).get("id")
        one_min_ago = datetime.datetime.utcnow() - datetime.timedelta(minutes=1)
        count = db.query(ActionRecord).filter(ActionRecord.actor_id==actor, ActionRecord.timestamp>=one_min_ago).count()
        if count > DEFAULT_RATE_LIMIT_PER_MIN:
            return False, f"actor rate {count}/min > {DEFAULT_RATE_LIMIT_PER_MIN}"
        return True, "rate ok"
    finally:
        db.close()

def confidence_check(action):
    conf = float(action.get("confidence") or 0.0)
    if conf < DEFAULT_CONFIDENCE_THRESHOLD:
        return False, f"confidence {conf} < threshold {DEFAULT_CONFIDENCE_THRESHOLD}"
    return True, "confidence ok"

def check_spending_limits(action, user_id):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id==user_id).first()
        if not user:
            return True, "no user spending limit"
        limit = user.spending_limit or 0.0
        cost = float(action.get("parameters",{}).get("cost", 0.0))
        first_of_month = datetime.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        total_spent = 0.0
        rows = db.query(ActionRecord).filter(ActionRecord.actor_id==user_id, ActionRecord.timestamp >= first_of_month).all()
        for r in rows:
            try:
                total_spent += float((r.parameters or {}).get("cost", 0.0))
            except:
                continue
        if limit > 0 and (total_spent + cost) > limit:
            return False, f"spending limit exceeded: {total_spent + cost} > {limit}"
        return True, "spending ok"
    finally:
        db.close()

def evaluate(action, user_id=None):
    flags = []
    wl_allowed, wl_reason = check_watchlists(action)
    if wl_allowed is False:
        log_audit(action.get("action_id"), user_id or "system", "rejected_blacklist", {"reason": wl_reason})
        return {"allowed": False, "require_approval": False, "reason": wl_reason, "flags": ["blacklist"]}
    if wl_allowed is True:
        flags.append("whitelist:"+wl_reason)

    ok_conf, conf_reason = confidence_check(action)
    if not ok_conf:
        flags.append("low_confidence")
        log_audit(action.get("action_id"), user_id or "system", "flag_low_confidence", {"reason": conf_reason})
        return {"allowed": True, "require_approval": True, "reason": conf_reason, "flags": flags}

    ok_rate, rate_reason = rate_check(action)
    if not ok_rate:
        flags.append("rate_anomaly")
        log_audit(action.get("action_id"), user_id or "system", "flag_rate", {"reason": rate_reason})
        return {"allowed": True, "require_approval": True, "reason": rate_reason, "flags": flags}

    ok_spend, spend_reason = check_spending_limits(action, user_id)
    if not ok_spend:
        log_audit(action.get("action_id"), user_id or "system", "rejected_spending", {"reason": spend_reason})
        return {"allowed": False, "require_approval": False, "reason": spend_reason, "flags": ["spending_exceeded"]}

    return {"allowed": True, "require_approval": False, "reason": "ok", "flags": flags}
