from fastapi import APIRouter, Header, HTTPException
from admin.api import AGENT_KEYS
from policy_engine import is_within_time_window
from audit import log_event

router = APIRouter(prefix="/agent")

def require(api_key: str, scope: str):
    if not api_key or api_key not in AGENT_KEYS:
        raise HTTPException(401, "Unknown agent key")

    agent = AGENT_KEYS[api_key]

    if scope not in agent["scopes"]:
        raise HTTPException(403, "Scope denied")

    if not is_within_time_window(agent.get("policy", {})):
        raise HTTPException(403, "Policy denied (time window)")

@router.get("/read")
def agent_read(x_api_key: str = Header(None)):
    require(x_api_key, "read")
    log_event(x_api_key, "read")
    return {"action": "read allowed"}

@router.post("/execute")
def agent_execute(x_api_key: str = Header(None)):
    require(x_api_key, "execute")
    log_event(x_api_key, "execute")
    return {"action": "execute allowed"}
