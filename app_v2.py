"""Main UAAL v2 app - cleaned and modularized but in-place for your prototype."""
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any
import datetime
import asyncio
import json
import requests

import adapters_extended as adapters
from db import SessionLocal, ActionRecord, User, Watchlist
import policy
import analytics
import anomalies
import replay
import auth

app = FastAPI(title="UAAL Prototype v2 - Enterprise (clean)")

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
    msg = {
        "type": event_type,
        "payload": payload,
        "ts": datetime.datetime.datetime.utcnow().isoformat(),
    }
    data = f"data: {json.dumps(msg)}\n\n"
    queues = list(_event_queues)
    for q in queues:
        try:
            await q.put(data)
        except Exception:
            _detach_event(q)


@app.get("/api/v1/stream")
async def event_stream():
    q = _attach_event()

    async def streamer():
        try:
            await q.put(
                f'data: {json.dumps({"type":"welcome","payload":{"msg":"connected"}})}\\n\\n'
            )
            while True:
                data = await q.get()
                yield data
        finally:
            _detach_event(q)

    return StreamingResponse(streamer(), media_type="text/event-stream")


# Request / models
class ReceiveAction(BaseModel):
    adapter: str
    agent_output: Dict[str, Any]
    require_approval: bool = False
    user_id: Optional[str] = None


@app.post("/api/v1/actions")
async def receive_action(
    payload: ReceiveAction, x_user_id: Optional[str] = Header(None)
):
    adapter_name = payload.adapter
    if adapter_name not in adapters.Adapters:
        raise HTTPException(status_code=400, detail=f"Unknown adapter: {adapter_name}")

    ua = adapters.Adapters[adapter_name](payload.agent_output)
    user_id = payload.user_id or x_user_id or ua["actor"].get("id")

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
            state="pending"
            if (payload.require_approval or result.get("require_approval"))
            else "executed",
            timestamp=datetime.datetime.datetime.utcnow(),
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
    await _broadcast_event(
        "action.received",
        {
            "action_id": row.action_id,
            "actor_id": row.actor_id,
            "verb": row.verb,
            "state": row.state,
        },
    )

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
            stored = (
                db.query(ActionRecord)
                .filter(ActionRecord.action_id == row.action_id)
                .first()
            )
            if stored:
                stored.delivered = True
                stored.deliveries = deliveries
                db.commit()
        finally:
            db.close()

        policy.log_audit(
            row.action_id, user_id or "system", "delivered", {"deliveries": deliveries}
        )
        await _broadcast_event(
            "action.delivered", {"action_id": row.action_id, "deliveries": deliveries}
        )

    return {
        "status": "ok",
        "action_id": row.action_id,
        "state": row.state,
        "policy": result,
    }


@app.get("/api/v1/actions")
async def list_actions(limit: int = 200):
    db = SessionLocal()
    try:
        rows = (
            db.query(ActionRecord)
            .order_by(ActionRecord.timestamp.desc())
            .limit(limit)
            .all()
        )
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
async def approve_action(action_id: str, x_user_id: Optional[str] = Header(None)):
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row:
            raise HTTPException(404, "Action not found")
        user = db.query(User).filter(User.id == (x_user_id or "")).first()
        if not user or user.role not in ("approver", "admin"):
            raise HTTPException(403, "Not authorized")
        row.state = "approved"
        db.commit()
        db.refresh(row)
    finally:
        db.close()

    await _broadcast_event(
        "action.approved", {"action_id": row.action_id, "actor_id": row.actor_id}
    )

    # deliver on approve
    deliveries = []
    for wid, w in WEBHOOKS.items():
        try:
            resp = requests.post(
                w["url"],
                json={
                    "action_id": row.action_id,
                    "actor_id": row.actor_id,
                    "verb": row.verb,
                    "parameters": row.parameters,
                },
                timeout=5,
            )
            deliveries.append({"webhook_id": wid, "status": resp.status_code})
        except Exception as exc:
            deliveries.append({"webhook_id": wid, "error": str(exc)})

    db = SessionLocal()
    try:
        stored = (
            db.query(ActionRecord)
            .filter(ActionRecord.action_id == row.action_id)
            .first()
        )
        if stored:
            stored.delivered = True
            stored.deliveries = deliveries
            db.commit()
    finally:
        db.close()

    policy.log_audit(
        action_id,
        x_user_id or "unknown",
        "approved_and_delivered",
        {"deliveries": deliveries},
    )
    return {"status": "approved", "deliveries": deliveries}


@app.post("/api/v1/actions/{action_id}/reject")
async def reject_action(action_id: str, x_user_id: Optional[str] = Header(None)):
    db = SessionLocal()
    try:
        row = db.query(ActionRecord).filter(ActionRecord.action_id == action_id).first()
        if not row:
            raise HTTPException(404, "Action not found")
        user = db.query(User).filter(User.id == (x_user_id or "")).first()
        if not user or user.role not in ("approver", "admin"):
            raise HTTPException(403, "Not authorized")
        row.state = "rejected"
        db.commit()
        db.refresh(row)
    finally:
        db.close()

    policy.log_audit(action_id, x_user_id or "unknown", "rejected", {})
    await _broadcast_event("action.rejected", {"action_id": action_id})
    return {"status": "rejected"}


@app.post("/api/v1/actions/{action_id}/undo")
async def undo_action(action_id: str, x_user_id: Optional[str] = Header(None)):
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
    policy.log_audit(action_id, x_user_id or "unknown", "undo", {})
    await _broadcast_event("action.undone", {"action_id": action_id})
    return {"status": "undone"}


@app.post("/api/v1/webhooks/register")
async def register_webhook(req: Request, x_user_id: Optional[str] = Header(None)):
    body = await req.json()
    webhook_id = body.get("id") or datetime.datetime.datetime.utcnow().isoformat()
    WEBHOOKS[webhook_id] = body
    policy.log_audit(
        "system",
        x_user_id or "system",
        "webhook_register",
        {"webhook_id": webhook_id, "body": body},
    )
    await _broadcast_event("webhook.registered", {"webhook_id": webhook_id})
    return {"status": "ok", "webhook_id": webhook_id}


# Admin helpers
class CreateUser(BaseModel):
    id: str
    display_name: str
    role: str = "viewer"
    spending_limit: float = 0.0


@app.post("/admin/users")
def create_user(u: CreateUser):
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.id == u.id).first()
        if existing:
            raise HTTPException(400, "user exists")
        user = User(
            id=u.id,
            display_name=u.display_name,
            role=u.role,
            spending_limit=u.spending_limit,
        )
        db.add(user)
        db.commit()
    finally:
        db.close()
    policy.log_audit(
        "system", u.id, "user_created", {"role": u.role, "limit": u.spending_limit}
    )
    return {"status": "ok", "user_id": u.id}


class WatchlistEntry(BaseModel):
    type: str
    field: str
    value: str


@app.post("/admin/watchlist")
def add_watchlist(entry: WatchlistEntry, x_user_id: Optional[str] = Header(None)):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == (x_user_id or "")).first()
        if not user or user.role != "admin":
            raise HTTPException(403, "forbidden")
        w = Watchlist(type=entry.type, field=entry.field, value=entry.value)
        db.add(w)
        db.commit()
    finally:
        db.close()
    policy.log_audit(
        "system", x_user_id or "unknown", "watchlist_add", {"entry": entry.dict()}
    )
    return {"status": "ok"}


# Metrics & analytics endpoints
@app.get("/api/v1/metrics/actions_per_agent")
def metrics_actions_per_agent(minutes: int = 60):
    return analytics.actions_per_agent(since_minutes=minutes)


@app.get("/api/v1/metrics/policy_violations")
def metrics_policy_violations(days: int = 30):
    return analytics.policy_violations(since_days=days)


@app.get("/api/v1/metrics/approval_queue")
def metrics_approval_queue():
    return analytics.approval_queue()


@app.get("/api/v1/metrics/spend_by_agent")
def metrics_spend_by_agent(months: int = 1):
    return analytics.spend_by_agent(months=months)


@app.get("/api/v1/anomalies/low_confidence")
def anomalies_low_confidence(threshold: float = 0.5, lookback_minutes: int = 60):
    return anomalies.low_confidence_alert(
        threshold=threshold, lookback_minutes=lookback_minutes
    )


@app.get("/api/v1/anomalies/zscore")
def anomalies_zscore(lookback: int = 500, z_threshold: float = 3.0):
    return anomalies.zscore_confidence_anomalies(
        lookback=lookback, z_threshold=z_threshold
    )


@app.post("/api/v1/replay/{action_id}")
def replay_action(action_id: str):
    return replay.replay_action(action_id, dry_run=True)


# Dev-only token endpoint (dev use)
@app.post("/admin/token")
def admin_token(user_id: str):
    token = auth.create_jwt(user_id, expires_in=86400)
    return {"token": token}


# Simple home
@app.get("/", response_class=HTMLResponse)
def root():
    return {"status": "UAAL v2 Enterprise running", "version": "2.0", "docs": "/docs"}


# Retry endpoints (requires redis + retry.py)
import retry
from fastapi import Response


@app.get("/admin/retries/count")
def retries_count():
    return {"count": retry.retry_count()}


@app.get("/admin/retries/peek")
def retries_peek(limit: int = 20):
    return {"items": retry.fetch_due(limit)}


# Simple API key endpoints (dev)
import apikeys


@app.post("/admin/api-keys/create")
def admin_api_key_create(payload: dict):
    owner = payload.get("owner", "unknown")
    scopes = payload.get("scopes", "")
    key = apikeys.create_key(owner=owner, scopes=scopes)
    return {"api_key": key, "owner": owner}


@app.post("/admin/api-keys/verify")
def admin_api_key_verify(payload: dict):
    raw = payload.get("key")
    ok = apikeys.verify_key(raw)
    return {"valid": bool(ok), "meta": ok}
