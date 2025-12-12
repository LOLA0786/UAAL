# UAAL — Universal Agent Action Layer (Prototype)

This repository holds the UAAL prototype — a normalization, governance and delivery layer
that lets autonomous agents act across applications with auditability and safety.

## Quickstart (local)
```bash
python3 -m venv venv.v2
source venv.v2/bin/activate
pip install -r requirements.txt
uvicorn app_v2:app --reload --port 8000

