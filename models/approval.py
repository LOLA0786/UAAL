from pydantic import BaseModel
import datetime
import uuid

class ApprovalRequest(BaseModel):
    id: str = str(uuid.uuid4())
    action_id: str
    reason: str
    requested_by: str
    status: str = "pending"
    created_at: datetime.datetime = datetime.datetime.utcnow()
    reviewed_by: str | None = None
    reviewed_at: datetime.datetime | None = None
