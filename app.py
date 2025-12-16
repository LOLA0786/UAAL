from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from admin.api import router as admin_router
from agent.api import router as agent_router

app = FastAPI(
    title="UAAL · Agent Authorization Control Plane",
    version="0.1.0"
)

# APIs
app.include_router(admin_router)
app.include_router(agent_router)

# Frontend
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def frontend():
    return FileResponse("static/index.html")
