from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import adapters
import datetime
import uuid

app = FastAPI(title="UAAL Prototype")

# in-memory stores (replace with DB in prod)
ACTIONS = {}
WEBHOOKS = {}


class ReceiveAction(BaseModel):
    adapter: str
    agent_output: dict
    require_approval: bool = False


@app.post("/api/v1/actions")
async def receive_action(payload: ReceiveAction):
    adapter_name = payload.adapter
    if adapter_name not in adapters.Adapters:
        raise HTTPException(status_code=400, detail=f"Unknown adapter: {adapter_name}")
    ua = adapters.Adapters[adapter_name](payload.agent_output)
    # default state: pending if require_approval else executed
    state = "pending" if payload.require_approval else "executed"
    ua_record = {**ua, "state": state, "delivered": False}
    ACTIONS[ua["action_id"]] = ua_record
    # if auto-execute, deliver to registered webhooks
    if state == "executed":
        await deliver_to_webhooks(ua_record)
    return {"status": "ok", "action_id": ua["action_id"], "state": state}


@app.get("/api/v1/actions")
async def list_actions():
    return list(ACTIONS.values())


@app.post("/api/v1/actions/{action_id}/approve")
async def approve_action(action_id: str):
    if action_id not in ACTIONS:
        raise HTTPException(404, "not found")
    ACTIONS[action_id]["state"] = "approved"
    await deliver_to_webhooks(ACTIONS[action_id])
    return {"status": "approved", "action_id": action_id}


@app.post("/api/v1/actions/{action_id}/undo")
async def undo_action(action_id: str):
    if action_id not in ACTIONS:
        raise HTTPException(404, "not found")
    # basic undo semantics: mark undone and store undo metadata
    ACTIONS[action_id]["state"] = "undone"
    ACTIONS[action_id]["undo_timestamp"] = datetime.datetime.utcnow().isoformat() + "Z"
    return {"status": "undone", "action_id": action_id}


@app.post("/api/v1/webhooks/register")
async def register_webhook(req: Request):
    body = await req.json()
    webhook_id = body.get("id") or str(uuid.uuid4())
    WEBHOOKS[webhook_id] = body
    return {"status": "ok", "webhook_id": webhook_id}


async def deliver_to_webhooks(action_record):
    # naive deliver: just mark delivered and append to webhook deliveries in record
    deliveries = []
    for wid, w in WEBHOOKS.items():
        # In a real system, you'd POST to w['url'] with retries, signatures, etc.
        deliveries.append(
            {
                "webhook_id": wid,
                "url": w.get("url"),
                "delivered_at": datetime.datetime.utcnow().isoformat() + "Z",
            }
        )
    action_record["delivered"] = True
    action_record.setdefault("deliveries", []).extend(deliveries)
    return deliveries
