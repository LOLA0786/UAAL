"""Governance helpers: 2FA and risk heuristics."""
from typing import Tuple, Dict, Any
import random
import string
import datetime

# Simple in-memory store for dev. Swap to DB or redis in prod.
_TWO_FA: Dict[str, Tuple[str, int]] = {}  # user_id -> (code, expiry_ts)


def generate_2fa(user_id: str, ttl: int = 300) -> str:
    code = "".join(random.choices(string.digits, k=6))
    expiry = int(
        (datetime.datetime.utcnow() + datetime.timedelta(seconds=ttl)).timestamp()
    )
    _TWO_FA[user_id] = (code, expiry)
    return code


def verify_2fa(user_id: str, code: str) -> bool:
    rec = _TWO_FA.get(user_id)
    if not rec:
        return False
    expected, expiry = rec
    if int(datetime.datetime.utcnow().timestamp()) > expiry:
        _TWO_FA.pop(user_id, None)
        return False
    if code == expected:
        _TWO_FA.pop(user_id, None)
        return True
    return False


def is_high_risk(action: Dict[str, Any]) -> bool:
    verb = (action.get("verb") or "").lower()
    objt = (action.get("object", {}).get("type") or "").lower()
    if any(k in verb for k in ("pay", "transfer", "charge", "delete", "remove")):
        return True
    if "payment" in objt or "billing" in objt:
        return True
    return False
