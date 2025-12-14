from models.approval import ApprovalRequest

APPROVAL_QUEUE: dict[str, ApprovalRequest] = {}

def enqueue(action_id, reason, requested_by):
    req = ApprovalRequest(
        action_id=action_id,
        reason=reason,
        requested_by=requested_by,
    )
    APPROVAL_QUEUE[req.id] = req
    return req

def approve(approval_id, reviewer):
    req = APPROVAL_QUEUE.get(approval_id)
    if not req:
        return None
    req.status = "approved"
    req.reviewed_by = reviewer
    return req

def reject(approval_id, reviewer):
    req = APPROVAL_QUEUE.get(approval_id)
    if not req:
        return None
    req.status = "rejected"
    req.reviewed_by = reviewer
    return req
