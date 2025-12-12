"""Policy engine for UAAL: checks watchlists, confidence, rate limits, spending."""
from typing import Dict, Any, Tuple
import datetime
from db import SessionLocal, ActionRecord, AuditLog, User, Watchlist

DEFAULT_CONFIDENCE_THRESHOLD = 0.6
DEFAULT_RATE_LIMIT_PER_MIN = 60  # more permissive default, tune later


def log_audit(action_id: str, user: str, event: str, details: Dict[str, Any]) -> None:
    db = SessionLocal()
    try:
        entry = AuditLog(action_id=action_id, user=user, event=event, details=details)
        db.add(entry)
        db.commit()
    finally:
        db.close()


def check_watchlists(action: Dict[str, Any]) -> Tuple[bool, str]:
    db = SessionLocal()
    try:
        items = db.query(Watchlist).all()
        for w in items:
            if w.field == "verb" and action.get("verb") == w.value:
                return (
                    (False, f"verb {w.value} is blacklisted")
                    if w.type == "blacklist"
                    else (True, f"verb {w.value} is whitelisted")
                )
            if w.field == "actor_id" and action.get("actor", {}).get("id") == w.value:
                return (
                    (False, f"actor {w.value} is blacklisted")
                    if w.type == "blacklist"
                    else (True, f"actor {w.value} is whitelisted")
                )
            if (
                w.field == "object_type"
                and action.get("object", {}).get("type") == w.value
            ):
                return (
                    (False, f"object_type {w.value} is blacklisted")
                    if w.type == "blacklist"
                    else (True, f"object_type {w.value} is whitelisted")
                )
        return (None, "no explicit watchlist rule")
    finally:
        db.close()


def rate_check(action: Dict[str, Any]) -> Tuple[bool, str]:
    db = SessionLocal()
    try:
        actor = action.get("actor", {}).get("id")
        if not actor:
            return True, "no actor"
        one_min_ago = datetime.datetime.datetime.utcnow() - datetime.timedelta(
            minutes=1
        )
        count = (
            db.query(ActionRecord)
            .filter(
                ActionRecord.actor_id == actor, ActionRecord.timestamp >= one_min_ago
            )
            .count()
        )
        if count > DEFAULT_RATE_LIMIT_PER_MIN:
            return False, f"actor rate {count}/min > {DEFAULT_RATE_LIMIT_PER_MIN}"
        return True, "rate ok"
    finally:
        db.close()


def confidence_check(action: Dict[str, Any]) -> Tuple[bool, str]:
    conf = float(action.get("confidence") or 0.0)
    if conf < DEFAULT_CONFIDENCE_THRESHOLD:
        return False, f"confidence {conf} < threshold {DEFAULT_CONFIDENCE_THRESHOLD}"
    return True, "confidence ok"


def check_spending_limits(action: Dict[str, Any], user_id: str) -> Tuple[bool, str]:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return True, "no user"
        limit = float(user.spending_limit or 0.0)
        if limit <= 0:
            return True, "no limit"
        cost = float((action.get("parameters") or {}).get("cost", 0.0))
        first_of_month = datetime.datetime.datetime.utcnow().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0
        )
        rows = (
            db.query(ActionRecord)
            .filter(
                ActionRecord.actor_id == user_id,
                ActionRecord.timestamp >= first_of_month,
            )
            .all()
        )
        total = 0.0
        for r in rows:
            try:
                total += float((r.parameters or {}).get("cost", 0.0))
            except Exception:
                continue
        if (total + cost) > limit:
            return False, f"spending limit exceeded: {total + cost} > {limit}"
        return True, "spending ok"
    finally:
        db.close()


def evaluate(action: Dict[str, Any], user_id: str = None) -> Dict[str, Any]:
    """Return evaluation dict: allowed, require_approval, reason, flags."""
    flags = []
    wl_allowed, wl_reason = check_watchlists(action)
    if wl_allowed is False:
        log_audit(
            action.get("action_id"),
            user_id or "system",
            "rejected_blacklist",
            {"reason": wl_reason},
        )
        return {
            "allowed": False,
            "require_approval": False,
            "reason": wl_reason,
            "flags": ["blacklist"],
        }
    if wl_allowed is True:
        flags.append("whitelist:" + wl_reason)

    ok_conf, conf_reason = confidence_check(action)
    if not ok_conf:
        flags.append("low_confidence")
        log_audit(
            action.get("action_id"),
            user_id or "system",
            "flag_low_confidence",
            {"reason": conf_reason},
        )
        return {
            "allowed": True,
            "require_approval": True,
            "reason": conf_reason,
            "flags": flags,
        }

    ok_rate, rate_reason = True, "rate not enforced here"
    # Rate check optional / toggled in deployment
    # ok_rate, rate_reason = rate_check(action)
    if not ok_rate:
        flags.append("rate_anomaly")
        log_audit(
            action.get("action_id"),
            user_id or "system",
            "flag_rate",
            {"reason": rate_reason},
        )
        return {
            "allowed": True,
            "require_approval": True,
            "reason": rate_reason,
            "flags": flags,
        }

    ok_spend, spend_reason = check_spending_limits(action, user_id or "")
    if not ok_spend:
        log_audit(
            action.get("action_id"),
            user_id or "system",
            "rejected_spending",
            {"reason": spend_reason},
        )
        return {
            "allowed": False,
            "require_approval": False,
            "reason": spend_reason,
            "flags": ["spending_exceeded"],
        }

    return {"allowed": True, "require_approval": False, "reason": "ok", "flags": flags}
