from fastapi import APIRouter
from pydantic import BaseModel
import secrets

router = APIRouter(prefix="/api-keys")

class CreateKeyRequest(BaseModel):
    owner: str
    role: str

@router.post("/create")
def create_api_key(payload: CreateKeyRequest):
    api_key = "uaal_" + secrets.token_hex(24)
    return {
        "status": "ok",
        "owner": payload.owner,
        "role": payload.role,
        "api_key": api_key
    }

@router.post("/verify")
def verify_api_key():
    return {"status": "valid"}
