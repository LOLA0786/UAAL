from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from apikeys import verify_api_key

EXEMPT_PATHS = (
    "/admin/api-keys",
    "/admin",
    "/docs",
    "/openapi.json",
)

class RBACMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        for p in EXEMPT_PATHS:
            if path.startswith(p):
                return await call_next(request)

        api_key = request.headers.get("x-api-key") or request.headers.get("authorization")
        if not api_key:
            raise HTTPException(status_code=401, detail="Missing API key")

        key_info = verify_api_key(api_key)
        if not key_info:
            raise HTTPException(status_code=401, detail="Invalid API key")

        request.state.api_key = key_info
        return await call_next(request)
