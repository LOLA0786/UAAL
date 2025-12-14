from pydantic import BaseModel
import uuid

class Organization(BaseModel):
    id: str = str(uuid.uuid4())
    name: str
    plan: str = "free"
    active: bool = True
