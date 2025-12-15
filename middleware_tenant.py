from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

# Routes that do NOT require tenant context
PUBLIC_PATH_PREFIXES = (
    "/docs",
    "/openapi.json",
    "/admin",
)

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Allow admin & public routes without tenant
        if path.startswith(PUBLIC_PATH_PREFIXES):
            return await call_next(request)

        # Tenant comes from API key (set by RBAC)
        api_key = getattr(request.state, "api_key", None)
        if not api_key:
            raise HTTPException(status_code=401, detail="Missing API context")

        # In v1: owner == tenant
        request.state.tenant = api_key["owner"]

        return await call_next(request)
