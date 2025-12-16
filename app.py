from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from agent.api import router as agent_router
from admin.api import router as admin_router
from storage import init_db
from sla import start_sla_worker
import os

app = FastAPI(title="UAAL · Enterprise Governance OS")

# -------------------------
# Startup hooks
# -------------------------
@app.on_event("startup")
def startup():
    init_db()
    start_sla_worker()

# -------------------------
# Routers
# -------------------------
app.include_router(admin_router)
app.include_router(agent_router)

# -------------------------
# Frontend
# -------------------------
STATIC_DIR = "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
def index():
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# -------------------------
# Health
# -------------------------
@app.get("/health")
def health():
    return {"status": "UAAL running"}
