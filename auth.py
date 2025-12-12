import os
import time
import hmac
import hashlib
from typing import Optional
from jose import jwt, JWTError
from functools import wraps
from db import SessionLocal, User
from fastapi import Header, HTTPException, Request

# configure these via env or fallback
JWT_SECRET = os.environ.get("UAAL_JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
API_KEY_HEADER = "x-api-key"

def create_jwt(subject: str, expires_in: int = 3600):
    now = int(time.time())
    payload = {"sub": subject, "iat": now, "exp": now + expires_in}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)

def decode_jwt(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        return None

def verify_api_key(api_key: str) -> bool:
    """
    Very small demo: API keys are stored as users with id==api_key in users table.
    Better: have separate ApiKey table with hashed key and metadata.
    """
    if not api_key:
        return False
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.id == api_key).first()
        return u is not None
    finally:
        db.close()

async def require_api_key(request: Request):
    apikey = request.headers.get(API_KEY_HEADER)
    if not apikey or not verify_api_key(apikey):
        raise HTTPException(401, "Missing or invalid API key")
    return apikey

def require_role(role_allowed: set):
    def _dep(x_user_id: Optional[str] = Header(None)):
        if not x_user_id:
            raise HTTPException(401, "Missing X-User-Id header")
        db = SessionLocal()
        try:
            u = db.query(User).filter(User.id == x_user_id).first()
            if not u or u.role not in role_allowed:
                raise HTTPException(403, "Forbidden")
            return u
        finally:
            db.close()
    return _dep
