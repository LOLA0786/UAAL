
# UAAL Prototype

Files:
- uas_schema.json : Universal Action Schema (JSON Schema)
- adapters.py : adapter functions converting agent outputs to UAS
- app.py : FastAPI prototype server with endpoints:
    - POST /api/v1/actions  (adapter, agent_output, require_approval)
    - GET  /api/v1/actions
    - POST /api/v1/actions/{action_id}/approve
    - POST /api/v1/actions/{action_id}/undo
    - POST /api/v1/webhooks/register

- agent_sdk.py : tiny Python SDK for agents to send outputs to UAAL

## Running locally (development)
1. Create virtualenv: `python -m venv venv && source venv/bin/activate`
2. Install deps: `pip install fastapi uvicorn pydantic requests`
3. Run server: `uvicorn app:app --reload --port 8000`
4. Use agent_sdk.send_to_uaal to send actions.

## Colab
Upload these files to Colab or git clone the repo, then run the server and the demo cells.

This is a minimal, educational prototype. For production you should:
- Replace in-memory stores with a database (Postgres, etc.)
- Add signatures and HMAC verification for webhooks
- Add role-based access control and audit logs
- Add persistent queues and retry logic for webhook deliveries
- Add policy engine and anomaly detection modules
- Add a UI/dashboard (React) to visualize actions, approvals, and undo flows
