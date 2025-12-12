"""
Simple 2FA simulation module.
In production, replace with SMS/Email provider and secure verification storage.
"""
import random
import time
import os

# in-memory store for demo; replace with Redis in prod
_OTP_STORE = {}

def send_otp(user_id: str, purpose: str = "approval", ttl_seconds: int = 300):
    code = str(random.randint(100000, 999999))
    _OTP_STORE[user_id] = {"code": code, "expires": time.time() + ttl_seconds, "purpose": purpose}
    # In production send via SMS / email. For now, return code to caller (dev mode).
    return {"sent": True, "otp": code}

def verify_otp(user_id: str, code: str):
    entry = _OTP_STORE.get(user_id)
    if not entry:
        return False
    if time.time() > entry["expires"]:
        _OTP_STORE.pop(user_id, None)
        return False
    ok = entry["code"] == code
    if ok:
        _OTP_STORE.pop(user_id, None)
    return ok
