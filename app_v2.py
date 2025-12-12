"""
UAAL v2 — Extended: Celery integration, WebSocket dashboard, 2FA approval flow, tenant support, compensator admin,
and replay sandbox (dry-run).
Ultra-Locked mode retained (all endpoints require auth).
"""
from fastapi import FastAPI, HTTPException, Request, Header, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, StreamingResponse, Response, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import datetime, asyncio, json, requests, logging

# internal modules
import adapters_extended as adapters
from db import SessionLocal, ActionRecord, User, Watchlist
import policy, analytics, anomalies, replay, auth, apikeys
import middleware_auth, middleware_rbac, middleware_tenant
import observability, twofactor, retry_backoff
from effectors.compensator import register_compensator, run_compensator

# Celery task enqueuer
from celery import Celery
import os
CELERY_BROKER = os.environ.get("CELERY_BROKER", "redis://localhost:6379/1")
CELERY_BACKEND = os.environ.get("CELERY_BACKEND", "redis://localhost:6379/2")
celery_app = Celery("uaal_worker", broker=CELERY_BROKER, backend=CELERY_BACKEND)

logger = logging.getLogger("uaal")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI(title="UAAL Prototype v2 - Ultra-Locked Extended", docs_url=None, redoc_url=None, openapi_url="/openapi.json")

# websocket manager
class WebSocketManager:
    def __init__(self):
        self.active: List[WebSocket] = []

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self.active.append(ws)

    def disconnect(self, ws: WebSocket):
        try: self.active.remove(ws)
        except ValueError: pass

    async def broadcast(self, msg: dict):
        to_remove = []
        for ws in list(self.active):
            try:
                await ws.send_text(json.dumps(msg))
            except Exception:
                to_remove.append(ws)
        for r in to_remove:
            self.disconnect(r)

ws_manager = WebSocketManager()

# models
class ReceiveAction(BaseModel):
    adapter: str
    agent_output: Dict[str, Any]
    require_approval: bool = False
    user_id: Optional[str] = None
    org_id: Optional[str] = None

class ApproveRequest(BaseModel):
    otp: str

# protected docs
@app.get("/docs", response_class=HTMLResponse)
def protected_docs(current_user: dict = Depends(middleware_auth.get_current_user)):
    return get_swagger_ui_html(openapi_url=app.openapi_url, title=f"{app.title} - Docs")

# websocket endpoint (protected)
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, current_user: dict = Depends(middleware_auth.get_current_user)):
    await ws_manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # echo for now
            await websocket.send_text(json.dumps({"echo": data}))
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)

# receive_action now enqueues to celery if execution allowed; enforces tenant header and 2FA for high-risk
@app.post("/api/v1/actions")
async def receive_action(payload: ReceiveAction, current_user: dict = Depends(middleware_auth.get_current_user), org: Optional[str] = Depends(middleware_tenant.get_current_org)):
    adapter_name = payload.adapter
    if adapter_name not in adapters.Adapters:
        raise HTTPException(status_code=400, detail=f"Unknown adapter: {adapter_name}")

    ua = adapters.Adapters[adapter_name](payload.agent_output)
    user_id = payload.user_id or current_user.get("id") or ua["actor"].get("id")
    org_id = payload.org_id or org or current_user.get("org_id") or None

    # Policy evaluation
    result = policy.evaluate(ua, user_id=user_id, org_id=org_id)

    # If policy flags high-risk and requires 2FA, initiate 2FA and mark pending_2fa
    if result.get("high_risk") and result.get("require_2fa"):
        twofactor_res = twofactor.send_otp(user_id, purpose="approve_action")
        # save to DB as pending_2fa with metadata
        db = SessionLocal()
        try:
            row = ActionRecord(
                action_id=ua["action_id"],
                actor_id=ua["actor"]["id"],
                actor_type=ua["actor"]["type"],
                verb=ua["verb"],
                object_type=ua["object"]["type"],
                object_id=ua["object"].get("id", ""),
                parameters=ua.get("parameters", {}),
                confidence=float(ua.get("confidence", 0.0) or 0.0),
                reasoning=ua.get("reasoning", ""),
                state="pending_2fa",
                timestamp=datetime.datetime.utcnow(),
                delivered=False,
                deliveries=[],
            )
            db.add(row); db.commit(); db.refresh(row)
        finally:
            db.close()
        await ws_manager.broadcast({"type":"action.pending_2fa", "action_id": row.action_id, "user": user_id})
        return {"status":"pending_2fa", "action_id": row.action_id, "otp_dev": twofactor_res.get("otp")}

    # normal path: create record and enqueue for delivery
    db = SessionLocal()
    try:
        row = ActionRecord(
            action_id=ua["action_id"],
            actor_id=ua["actor"]["id"],
            actor_type=ua["actor"]["type"],
            verb=ua["verb"],
            object_type=ua["object"]["type"],
            object_id=ua["object"].get("id", ""),
            parameters=ua.get("parameters", {}),
            confidence=float(ua.get("confidence", 0.0) or 0.0),
            reasoning=ua.get("reasoning", ""),
            state="queued",
            timestamp=datetime.datetime.utcnow(),
            delivered=False,
            deliveries=[],
            org_id = org_id if hasattr(ActionRecord, "org_id") else None
        )
        db.add(row); db.commit(); db.refresh(row)
    finally:
        db.close()

    # metrics
    observability.ACTION_COUNTER.labels(actor_id=user_id).inc()
    await ws_manager.broadcast({"type":"action.queued", "action_id": row.action_id})

    # Enqueue to Celery
    try:
        celery_app.send_task("celery_worker.deliver_action", args=[row.action_id])
    except Exception as exc:
        retry_backoff.push_retry({"action_id": row.action_id, "error": str(exc)}, attempt=1)

    return {"status":"queued", "action_id": row.action_id, "policy": result}

# Endpoint to finalize 2FA approval
@app.post("/api/v1/actions/{action_id}/finalize_2fa")
def finalize_2fa(action_id: str, payload: ApproveRequest, current_user: dict = Depends(middleware_auth.get_current_user)):
    user_id = current_user.get("id")
    if not twofactor.verify_otp(user_id, payload.otp):
        raise HTTPException(status_code=403, detail="invalid otp")
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row or row.state != "pending_2fa":
            raise HTTPException(404, "Action not found or not pending_2fa")
        row.state = "queued"
        db.commit(); db.refresh(row)
    finally:
        db.close()
    # enqueue
    celery_app.send_task("celery_worker.deliver_action", args=[action_id])
    return {"status":"queued", "action_id": action_id}

# replay sandbox (dry-run)
@app.post("/api/v1/replay/{action_id}")
def replay_action(action_id: str, dry_run: bool = True, current_user: dict = Depends(middleware_auth.get_current_user)):
    # replay.replay_action should handle dry_run flag and not perform external side effects
    res = replay.replay_action(action_id, dry_run=dry_run)
    return {"action_id": action_id, "dry_run": dry_run, "result": res}

# Compensator run (admin-protected)
@app.post("/admin/compensator/run/{action_id}")
def admin_run_compensator(action_id: str, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role("admin"))):
    res = run_compensator(action_id)
    if res.get("status") == "not_found":
        raise HTTPException(status_code=404, detail="compensator not found")
    return res

# list actions - enforce tenant isolation (if org header present)
@app.get("/api/v1/actions")
def list_actions(limit: int = 200, current_user: dict = Depends(middleware_auth.get_current_user), org: Optional[str] = Depends(middleware_tenant.get_current_org)):
    db = SessionLocal()
    try:
        q = db.query(ActionRecord).order_by(ActionRecord.timestamp.desc())
        if org:
            # assume ActionRecord has org_id column; if not, this is a no-op
            try:
                q = q.filter(ActionRecord.org_id == org)
            except Exception:
                pass
        rows = q.limit(limit).all()
        return [
            {
                "action_id": r.action_id,
                "actor_id": r.actor_id,
                "actor_type": r.actor_type,
                "verb": r.verb,
                "object_type": r.object_type,
                "object_id": r.object_id,
                "parameters": r.parameters,
                "confidence": r.confidence,
                "reasoning": r.reasoning,
                "state": r.state,
                "timestamp": r.timestamp.isoformat(),
                "delivered": r.delivered,
                "deliveries": r.deliveries,
                "org_id": getattr(r, "org_id", None),
            }
            for r in rows
        ]
    finally:
        db.close()

# simple root
@app.get("/", response_class=JSONResponse)
def root(current_user: dict = Depends(middleware_auth.get_current_user)):
    return {"status": "UAAL v2 Enterprise running (extended)", "version": "2.1"}
