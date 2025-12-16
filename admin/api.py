from fastapi import APIRouter, Depends
from pydantic import BaseModel
from auth import require_admin
import secrets

router = APIRouter(prefix="/admin", tags=["admin"])

API_KEYS = {}

class CreateAgentRequest(BaseModel):
    owner: str = "demo"
    role: str = "agent"
    name: str | None = None

@router.post("/api-keys/create")
def create_api_key(
    payload: CreateAgentRequest,
    admin=Depends(require_admin)
):
    key = secrets.token_hex(16)

    API_KEYS[key] = {
        "owner": payload.owner,
        "role": payload.role,
        "name": payload.name,
        "active": True
    }

    return {
        "api_key": key,
        "owner": payload.owner,
        "role": payload.role,
        "name": payload.name
    }

@router.get("/audit")
def audit(admin=Depends(require_admin)):
    return {
        "total_keys": len(API_KEYS),
        "keys": API_KEYS
    }
