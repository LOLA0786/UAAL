"""API key utilities and simple CLI to create keys in DB (dev only)."""
import secrets
import hashlib
from db import SessionLocal, Base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from typing import Optional

# local simple table - if your db.py defines Base, skip duplicate table
from db import engine
from sqlalchemy.orm import sessionmaker

LocalBase = Base


class ApiKey(LocalBase):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True, index=True)
    owner = Column(String, index=True)
    scopes = Column(String, default="")
    disabled = Column(Boolean, default=False)


def create_key(owner: str, scopes: str = "") -> str:
    raw = secrets.token_urlsafe(32)
    # store hashed key in DB (simple sha256)
    hashed = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    db = SessionLocal()
    try:
        k = ApiKey(key=hashed, owner=owner, scopes=scopes, disabled=False)
        db.add(k)
        db.commit()
    finally:
        db.close()
    return raw


def verify_key(raw_key: str) -> Optional[dict]:
    if not raw_key:
        return None
    import hashlib

    hashed = hashlib.sha256(raw_key.encode("utf-8")).hexdigest()
    db = SessionLocal()
    try:
        rec = (
            db.query(ApiKey)
            .filter(ApiKey.key == hashed, ApiKey.disabled == False)
            .first()
        )
        if not rec:
            return None
        return {"owner": rec.owner, "scopes": rec.scopes}
    finally:
        db.close()


# create table if not existing
LocalBase.metadata.create_all(bind=engine)
