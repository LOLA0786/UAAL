"""
Authentication middleware helpers for UAAL.

Provides:
- get_current_user dependency for FastAPI endpoints
- supports Authorization: Bearer <jwt> and X-API-Key (x-api-key) header
- returns a dict: {"id": <id>, "role": <role>, "type": "user|api_key"} or raises HTTPException(401)
"""

from typing import Optional, Dict, Any
import os
from fastapi import Header, HTTPException, Depends, Request
from jose import JWTError
import auth
import apikeys
from db import SessionLocal, User

def _get_user_from_db(user_id: str) -> Optional[Dict[str, Any]]:
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.id == user_id).first()
        if not u:
            return None
        return {"id": u.id, "display_name": u.display_name, "role": u.role}
    finally:
        db.close()


async def get_current_user(request: Request, authorization: Optional[str] = Header(None), x_api_key: Optional[str] = Header(None)):
    """
    FastAPI dependency. Resolve either:
    - Bearer JWT in Authorization header
    - x-api-key header (raw key)
    Returns a user dict with at least 'id' and 'role'.
    """

    # 1) API key path
    if x_api_key:
        meta = apikeys.verify_key(x_api_key)
        if not meta:
            raise HTTPException(status_code=401, detail="Invalid API key")
        # meta contains owner and scopes; owner may map to a user id
        owner = meta.get("owner") or "api_key"
        # attempt to load user role if exists
        u = _get_user_from_db(owner)
        role = u["role"] if u else "agent"
        return {"id": owner, "role": role, "type": "api_key", "scopes": meta.get("scopes", "")}

    # 2) Bearer JWT path
    if authorization:
        # expected "Bearer <token>"
        try:
            parts = authorization.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise HTTPException(status_code=401, detail="Invalid Authorization header")
            token = parts[1]
            payload = auth.decode_jwt(token)
            if not payload:
                raise HTTPException(status_code=401, detail="Invalid or expired token")
            sub = payload.get("sub")
            if not sub:
                raise HTTPException(status_code=401, detail="Invalid token payload")
            u = _get_user_from_db(sub)
            if not u:
                # allow token-based user even if no DB row; default role=viewer
                return {"id": sub, "role": "viewer", "type": "jwt"}
            return {"id": u["id"], "display_name": u.get("display_name"), "role": u.get("role"), "type": "jwt"}
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    # 3) fallback: unauthenticated
    raise HTTPException(status_code=401, detail="Missing credentials; provide x-api-key or Authorization bearer token")
