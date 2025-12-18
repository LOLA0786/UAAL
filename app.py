from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from uaal_prototype.admin.api_emit import router as emit_router
from uaal_prototype.admin.api_emit_failure import router as emit_failure_router
from uaal_prototype.admin.api_list import router as list_router
from uaal_prototype.admin.api_verify import router as verify_router
from uaal_prototype.admin.api_replay import router as replay_router
from uaal_prototype.admin.api_tamper import router as tamper_router
from uaal_prototype.admin.api_status import router as status_router
from uaal_prototype.admin.api_metrics import router as metrics_router

app = FastAPI(title="UAAL")

# ✅ API routes FIRST
app.include_router(emit_router)
app.include_router(emit_failure_router)
app.include_router(list_router)
app.include_router(verify_router)
app.include_router(replay_router)
app.include_router(tamper_router)
app.include_router(status_router)
app.include_router(metrics_router)

# ✅ UI served at /ui (not /)
app.mount("/ui", StaticFiles(directory="uaal_prototype/static", html=True), name="ui")

from uaal_prototype.admin.api_audit import router as audit_router
app.include_router(audit_router)
