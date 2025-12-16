# UAAL — Agent Authorization & Governance OS

UAAL is the control plane enterprises put **around AI agents**.

Agents do not execute blindly.
They are authorized, simulated, approved, or rejected — with full auditability.

---

## Why UAAL Exists

As AI agents gain autonomy, enterprises need:
- policy enforcement
- human-in-the-loop control
- audit trails
- compliance alignment (SOC-2)

UAAL provides this as infrastructure.

---

## Core Capabilities

- Agent action gateway
- Policy engine (per org)
- Human approvals with SLA
- Multi-agent dependency graph
- Signed policy bundles
- Full audit log + export
- SOC-2 control mapping

---

## Demo (3 Commands)

```bash
python3 -m venv venv
source venv/bin/activate
pip install fastapi uvicorn
python3 -m uvicorn app:app

