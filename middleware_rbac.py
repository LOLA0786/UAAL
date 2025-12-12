"""
Role-based access control helpers.

Provides:
- require_role dependency factory that can be used in endpoint signatures.
Usage:
    from middleware_rbac import require_role
    @app.post("/admin/secure")
    def secure_endpoint(current_user = Depends(get_current_user), _ = Depends(require_role("admin"))):
        ...
"""

from typing import Callable
from fastapi import Depends, HTTPException
import middleware_auth

def require_role(role: str):
    """
    Dependency that raises HTTPException(403) if current_user.role is not sufficient.
    Example: Depends(require_role("admin"))
    """
    def _inner(current_user = Depends(middleware_auth.get_current_user)):
        user_role = current_user.get("role") if current_user else None
        # simple hierarchical roles can be extended; for now exact match or admin override
        if not user_role:
            raise HTTPException(status_code=403, detail="Missing role")
        if user_role == "admin":
            return True
        if user_role != role:
            raise HTTPException(status_code=403, detail=f"Requires role: {role}")
        return True
    return _inner
