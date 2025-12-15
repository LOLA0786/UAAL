from fastapi import APIRouter, Header, HTTPException

router = APIRouter(prefix="/agent")

@router.get("/ping")
def agent_ping(x_api_key: str = Header(None)):
    if not x_api_key or not x_api_key.startswith("uaal_"):
        raise HTTPException(status_code=401, detail="Invalid agent key")
    return {"status": "agent alive"}
