from pydantic import BaseModel

class AgentIntent(BaseModel):
    actor_id: str
    verb: str
    target: dict
    parameters: dict = {}
    confidence: float | None = None
