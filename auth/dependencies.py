from fastapi import Header, HTTPException, status
import os

DEMO_MODE = os.getenv("UAAL_DEMO_MODE", "true").lower() == "true"
DEMO_ADMIN_KEY = os.getenv("UAAL_ADMIN_KEY", "demo-admin-key")

def require_admin(
    x_api_key: str = Header(None),
    authorization: str = Header(None),
):
    # 🚨 INVESTOR DEMO MODE: NEVER BLOCK
    if DEMO_MODE:
        return True

    # ---- PRODUCTION MODE BELOW ----
    provided_key = None

    if x_api_key:
        provided_key = x_api_key

    if authorization and authorization.lower().startswith("bearer "):
        provided_key = authorization.split(" ", 1)[1].strip()

    if not provided_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing admin API key"
        )

    if provided_key != DEMO_ADMIN_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin API key"
        )

    return True
