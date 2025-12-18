import json
import os

STORE_FILE = "approvals_store.json"

def _load():
    if not os.path.exists(STORE_FILE):
        return {}
    with open(STORE_FILE) as f:
        return json.load(f)

def _save(data):
    with open(STORE_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_request(record):
    data = _load()
    data[record["approval_id"]] = record
    _save(data)

def load_request(approval_id):
    return _load().get(approval_id)

def update_status(record):
    data = _load()
    data[record["approval_id"]] = record
    _save(data)
