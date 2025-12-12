"""
UAAL v2 - Strict (Ultra-Locked) app_v2.py

All endpoints require authentication via:
 - Authorization: Bearer <JWT>
 OR
 - x-api-key: <raw-api-key>

Admin-only endpoints additionally require role == "admin".
Approver endpoints require role == "approver" or "admin".

This file is a drop-in replacement. Restart uvicorn after replacing.
"""
from fastapi import FastAPI, HTTPException, Request, Header, Depends
from fastapi.responses import HTMLResponse, StreamingResponse, Response, JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from pydantic import BaseModel
from typing import Optional, Dict, Any
import datetime
import asyncio
import json
import requests
import logging

import adapters_extended as adapters
from db import SessionLocal, ActionRecord, User, Watchlist
import policy
import analytics
import anomalies
import replay
import auth
import middleware_auth
import middleware_rbac
import apikeys

# Configure logging
logger = logging.getLogger("uaal")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
    logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = FastAPI(title="UAAL Prototype v2 - Ultra-Locked", docs_url=None, redoc_url=None, openapi_url="/openapi.json")

# Simple in-memory webhook store for demo
WEBHOOKS: Dict[str, Dict[str, Any]] = {}

# SSE support
_event_queues = []


def _attach_event() -> asyncio.Queue:
    q: asyncio.Queue = asyncio.Queue()
    _event_queues.append(q)
    return q


def _detach_event(q: asyncio.Queue) -> None:
    try:
        _event_queues.remove(q)
    except Exception:
        pass


async def _broadcast_event(event_type: str, payload: Dict[str, Any]) -> None:
    msg = {"type": event_type, "payload": payload, "ts": datetime.datetime.utcnow().isoformat()}
    data = f"data: {json.dumps(msg)}\n\n"
    queues = list(_event_queues)
    for q in queues:
        try:
            await q.put(data)
        except Exception:
            _detach_event(q)


# Request / models
class ReceiveAction(BaseModel):
    adapter: str
    agent_output: Dict[str, Any]
    require_approval: bool = False
    user_id: Optional[str] = None


class CreateUser(BaseModel):
    id: str
    display_name: str
    role: str = "viewer"
    spending_limit: float = 0.0


class WatchlistEntry(BaseModel):
    type: str
    field: str
    value: str


# Protected docs route (requires auth)
@app.get("/docs", response_class=HTMLResponse)
def protected_docs(current_user: dict = Depends(middleware_auth.get_current_user)):
    """
    Serve the Swagger UI only if authenticated.
    """
    return get_swagger_ui_html(openapi_url=app.openapi_url, title=f"{app.title} - Docs")


# SSE endpoint (requires auth)
@app.get("/api/v1/stream")
async def event_stream(current_user: dict = Depends(middleware_auth.get_current_user)):
    q = _attach_event()

    async def streamer():
        try:
            await q.put(f'data: {json.dumps({"type":"welcome","payload":{"msg":"connected"}})}\\n\\n')
            while True:
                data = await q.get()
                yield data
        finally:
            _detach_event(q)

    return StreamingResponse(streamer(), media_type="text/event-stream")


@app.post("/api/v1/actions")
async def receive_action(payload: ReceiveAction, current_user: dict = Depends(middleware_auth.get_current_user)):
    adapter_name = payload.adapter
    if adapter_name not in adapters.Adapters:
        raise HTTPException(status_code=400, detail=f"Unknown adapter: {adapter_name}")

    ua = adapters.Adapters[adapter_name](payload.agent_output)
    # prefer explicit user_id or current_user id
    user_id = payload.user_id or current_user.get("id") or ua["actor"].get("id")

    # Policy evaluation
    result = policy.evaluate(ua, user_id=user_id)

    # Save to DB
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
            state="pending" if (payload.require_approval or result.get("require_approval")) else "executed",
            timestamp=datetime.datetime.utcnow(),
            delivered=False,
            deliveries=[],
        )
        db.add(row)
        db.commit()
        db.refresh(row)
    finally:
        db.close()

    policy.log_audit(row.action_id, user_id or "system", "received", {"policy": result})

    # Broadcast new action
    await _broadcast_event("action.received", {"action_id": row.action_id, "actor_id": row.actor_id, "verb": row.verb, "state": row.state})

    # Auto-deliver if allowed and executed
    if row.state == "executed" and result.get("allowed", True):
        deliveries = []
        for wid, w in WEBHOOKS.items():
            try:
                resp = requests.post(
                    w["url"],
                    json={
                        "action_id": row.action_id,
                        "actor_id": row.actor_id,
                        "verb": row.verb,
                        "object_type": row.object_type,
                        "parameters": row.parameters,
                    },
                    timeout=5,
                )
                deliveries.append({"webhook_id": wid, "status": resp.status_code})
            except Exception as exc:
                deliveries.append({"webhook_id": wid, "error": str(exc)})
        db = SessionLocal()
        try:
            stored = db.query(ActionRecord).filter(ActionRecord.action_id == row.action_id).first()
            if stored:
                stored.delivered = True
                stored.deliveries = deliveries
                db.commit()
        finally:
            db.close()

        policy.log_audit(row.action_id, user_id or "system", "delivered", {"deliveries": deliveries})
        await _broadcast_event("action.delivered", {"action_id": row.action_id, "deliveries": deliveries})

    return {"status": "ok", "action_id": row.action_id, "state": row.state, "policy": result}


@app.get("/api/v1/actions")
def list_actions(limit: int = 200, current_user: dict = Depends(middleware_auth.get_current_user)):
    db = SessionLocal()
    try:
        rows = db.query(ActionRecord).order_by(ActionRecord.timestamp.desc()).limit(limit).all()
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
            }
            for r in rows
        ]
    finally:
        db.close()


@app.post("/api/v1/actions/{action_id}/approve")
async def approve_action(
    action_id: str,
    current_user: dict = Depends(middleware_auth.get_current_user),
    _=Depends(middleware_rbac.require_role("approver")),
):
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row:
            raise HTTPException(404, "Action not found")
        row.state = "approved"
        db.commit()
        db.refresh(row)
    finally:
        db.close()

    await _broadcast_event("action.approved", {"action_id": row.action_id, "actor_id": row.actor_id})

    # deliver on approve
    deliveries = []
    for wid, w in WEBHOOKS.items():
        try:
            resp = requests.post(
                w["url"],
                json={"action_id": row.action_id, "actor_id": row.actor_id, "verb": row.verb, "parameters": row.parameters},
                timeout=5,
            )
            deliveries.append({"webhook_id": wid, "status": resp.status_code})
        except Exception as exc:
            deliveries.append({"webhook_id": wid, "error": str(exc)})

    db = SessionLocal()
    try:
        stored = db.query(ActionRecord).filter(ActionRecord.action_id == row.action_id).first()
        if stored:
            stored.delivered = True
            stored.deliveries = deliveries
            db.commit()
    finally:
        db.close()

    policy.log_audit(action_id, current_user.get("id") or "unknown", "approved_and_delivered", {"deliveries": deliveries})
    return {"status": "approved", "deliveries": deliveries}


@app.post("/api/v1/actions/{action_id}/reject")
async def reject_action(
    action_id: str,
    current_user: dict = Depends(middleware_auth.get_current_user),
    _=Depends(middleware_rbac.require_role("approver")),
):
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row:
            raise HTTPException(404, "Action not found")
        row.state = "rejected"
        db.commit()
        db.refresh(row)
    finally:
        db.close()

    policy.log_audit(action_id, current_user.get("id") or "unknown", "rejected", {})
    await _broadcast_event("action.rejected", {"action_id": action_id})
    return {"status": "rejected"}


@app.post("/api/v1/actions/{action_id}/undo")
async def undo_action(action_id: str, current_user: dict = Depends(middleware_auth.get_current_user)):
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row:
            raise HTTPException(404, "Action not found")
        row.state = "undone"
        db.commit()
        db.refresh(row)
    finally:
        db.close()
    policy.log_audit(action_id, current_user.get("id") or "unknown", "undo", {})
    await _broadcast_event("action.undone", {"action_id": action_id})
    return {"status": "undone"}


@app.post("/api/v1/webhooks/register")
async def register_webhook(req: Request, current_user: dict = Depends(middleware_auth.get_current_user)):
    body = await req.json()
    webhook_id = body.get("id") or datetime.datetime.utcnow().isoformat()
    WEBHOOKS[webhook_id] = body
    policy.log_audit("system", current_user.get("id") or "system", "webhook_register", {"webhook_id": webhook_id, "body": body})
    await _broadcast_event("webhook.registered", {"webhook_id": webhook_id})
    return {"status": "ok", "webhook_id": webhook_id}


@app.post("/admin/users")
def create_user(u: CreateUser, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role("admin"))):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.id == u.id).first()
        if existing:
            raise HTTPException(400, "user exists")
        user = User(id=u.id, display_name=u.display_name, role=u.role, spending_limit=u.spending_limit)
        db.add(user)
        db.commit()
    finally:
        db.close()
    policy.log_audit("system", u.id, "user_created", {"role": u.role, "limit": u.spending_limit})
    return {"status": "ok", "user_id": u.id}


@app.post("/admin/watchlist")
def add_watchlist(entry: WatchlistEntry, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role("admin"))):
    db = SessionLocal()
    try:
        w = Watchlist(type=entry.type, field=entry.field, value=entry.value)
        db.add(w)
        db.commit()
    finally:
        db.close()
    policy.log_audit("system", current_user.get("id") or "unknown", "watchlist_add", {"entry": entry.dict()})
    return {"status": "ok"}


# Metrics & analytics endpoints (protected)
@app.get("/api/v1/metrics/actions_per_agent")
def metrics_actions_per_agent(minutes: int = 60, current_user: dict = Depends(middleware_auth.get_current_user)):
    return analytics.actions_per_agent(since_minutes=minutes)


@app.get("/api/v1/metrics/policy_violations")
def metrics_policy_violations(days: int = 30, current_user: dict = Depends(middleware_auth.get_current_user)):
    return analytics.policy_violations(since_days=days)


@app.get("/api/v1/metrics/approval_queue")
def metrics_approval_queue(current_user: dict = Depends(middleware_auth.get_current_user)):
    return analytics.approval_queue()


@app.get("/api/v1/metrics/spend_by_agent")
def metrics_spend_by_agent(months: int = 1, current_user: dict = Depends(middleware_auth.get_current_user)):
    return analytics.spend_by_agent(months=months)


@app.get("/api/v1/anomalies/low_confidence")
def anomalies_low_confidence(threshold: float = 0.5, lookback_minutes: int = 60, current_user: dict = Depends(middleware_auth.get_current_user)):
    return anomalies.low_confidence_alert(threshold=threshold, lookback_minutes=lookback_minutes)


@app.get("/api/v1/anomalies/zscore")
def anomalies_zscore(lookback: int = 500, z_threshold: float = 3.0, current_user: dict = Depends(middleware_auth.get_current_user)):
    return anomalies.zscore_confidence_anomalies(lookback=lookback, z_threshold=z_threshold)


@app.post("/api/v1/replay/{action_id}")
def replay_action(action_id: str, current_user: dict = Depends(middleware_auth.get_current_user)):
    return replay.replay_action(action_id, dry_run=True)


# Admin API key endpoints (admin only)
@app.post("/admin/api-keys/create")
def admin_api_key_create(payload: dict, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role("admin"))):
    owner = payload.get("owner", "unknown")
    scopes = payload.get("scopes", "")
    key = apikeys.create_key(owner=owner, scopes=scopes)
    return {"api_key": key, "owner": owner}


@app.post("/admin/api-keys/verify")
def admin_api_key_verify(payload: dict, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role("admin"))):
    raw = payload.get("key")
    ok = apikeys.verify_key(raw)
    return {"valid": bool(ok), "meta": ok}


# Dev-only token endpoint (dev use) - admin only for ultra-locked
@app.post("/admin/token")
def admin_token(user_id: str, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role("admin"))):
    token = auth.create_jwt(user_id, expires_in=86400)
    return {"token": token}


# Simple home - protected
@app.get("/", response_class=JSONResponse)
def root(current_user: dict = Depends(middleware_auth.get_current_user)):
    return {"status": "UAAL v2 Enterprise running", "version": "2.0", "docs": "/docs"}



# ---- Prometheus metrics endpoint (protected) ----
import observability
from fastapi.responses import Response

@app.get("/metrics")
def metrics(current_user: dict = Depends(middleware_auth.get_current_user)):
    """
    Expose Prometheus metrics. Protected by auth in Ultra-Locked Mode.
    """
    data = observability.metrics_response()
    return Response(content=data, media_type="text/plain")
