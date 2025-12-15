"""
Auth middleware for UAAL
Enforces API key / bearer token before action execution
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from apikeys import verify_api_key


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Public endpoints
        if request.url.path in ("/", "/docs", "/openapi.json"):
            return await call_next(request)

        api_key = request.headers.get("x-api-key")
        auth_header = request.headers.get("Authorization")

        if not api_key and not auth_header:
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing credentials; provide x-api-key or Authorization bearer token"},
            )

        if api_key and not verify_api_key(api_key):
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid API key"},
            )

        return await call_next(request)
