"""
Simple tenant extractor/enforcer.
Adds 'org_id' to request state via dependency for endpoints to use.
"""
from fastapi import Header, HTTPException, Request

async def get_current_org(request: Request, x_org_id: str | None = Header(None)):
    if not x_org_id:
        # optional: allow system-level requests if you must
        # raise HTTPException(status_code=400, detail="Missing X-Org-Id header")
        request.state.org_id = None
        return None
    # You can add DB validation here to check tenant exists
    request.state.org_id = x_org_id
    return x_org_id
