from fastapi import FastAPI

from models import init_db
from admin.api import router as admin_router
from agent.api import router as agent_router

# Initialize DB (idempotent)
init_db()

app = FastAPI(title="UAAL")

app.include_router(admin_router, prefix="/admin")
app.include_router(agent_router, prefix="/agent")

@app.get("/health")
def health():
    return {"status": "ok"}
