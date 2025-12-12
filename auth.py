"""Authentication helpers: API-Key verification and JWT creation/decoding."""
from typing import Optional, Dict, Any
import os
import time
from jose import jwt, JWTError
from db import SessionLocal, User

JWT_SECRET = os.environ.get("UAAL_JWT_SECRET", "dev-secret-change-me")
JWT_ALG = "HS256"
API_KEY_HEADER = "x-api-key"


def create_jwt(subject: str, expires_in: int = 3600) -> str:
    now = int(time.time())
    payload = {"sub": subject, "iat": now, "exp": now + expires_in}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALG)


def decode_jwt(token: str) -> Optional[Dict[str, Any]]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALG])
    except JWTError:
        return None


def verify_api_key(api_key: Optional[str]) -> bool:
    if not api_key:
        return False
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.id == api_key).first()
        return u is not None
    finally:
        db.close()
