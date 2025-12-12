# UAAL — Universal Agent Action Layer

Short: UAAL normalizes agent outputs into a Universal Action Schema (UAS), evaluates policies, logs auditable traces, and safely routes actions to effectors.

## What’s included
- FastAPI core (`app_v2.py`) with RBAC and API-key/JWT auth.
- Adapters + SDK scaffolding.
- Observability: Prometheus metrics + Grafana dashboards (provisioning).
- Retry queue (Redis) + Celery worker skeleton.
- Kafka producer hook.
- ML anomaly detector (IsolationForest bootstrap).
- CI (GitHub Actions).
- Docker + k8s starter manifests.

## Quick start (local dev)
1. Install Python 3.10+, create venv:

