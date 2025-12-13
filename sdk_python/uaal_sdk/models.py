from typing import Any, Dict
from pydantic import BaseModel


class ActionResult(BaseModel):
    action_id: str
    state: str
    policy: Dict[str, Any]


class ActionRequest(BaseModel):
    verb: str
    object_type: str
    parameters: Dict[str, Any]
