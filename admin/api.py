from fastapi import APIRouter
from pydantic import BaseModel
import secrets
from store import load_keys, save_keys

router = APIRouter(prefix="/api-keys")
AGENT_KEYS = load_keys()

class CreateKeyRequest(BaseModel):
    owner: str
    role: str
    scopes: list[str]
    policy: dict = {}

@router.post("/create")
def create_api_key(payload: CreateKeyRequest):
    api_key = "uaal_" + secrets.token_hex(16)
    AGENT_KEYS[api_key] = payload.dict()
    save_keys(AGENT_KEYS)
    return {"api_key": api_key, "policy": payload.policy}

@router.get("/audit")
def audit():
    return AGENT_KEYS
