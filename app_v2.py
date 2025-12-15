from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import existing core app
import app as core_app

# Import admin API (single router)
from admin.api import router as admin_router

# Middleware
from middleware_auth import AuthMiddleware
from middleware_tenant import TenantMiddleware
from middleware_rbac import RBACMiddleware

app = FastAPI(
    title="UAAL – Universal Agent Action Layer",
    version="0.2.0",
)

# ---- Middleware ----
app.add_middleware(AuthMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(RBACMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Mount core API ----
app.mount("/api", core_app.app)

# ---- Mount admin API ----
app.include_router(admin_router)

@app.get("/")
def root():
    return {"status": "UAAL live", "mode": "governed autonomy"}

