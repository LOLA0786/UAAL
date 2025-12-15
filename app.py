from fastapi import FastAPI
from admin.api import router as admin_router
from agent.api import router as agent_router

app = FastAPI(title="UAAL Prototype")

app.include_router(admin_router, prefix="/admin")
app.include_router(agent_router)
