import json
import os

STORE_FILE = "agent_keys.json"

def load_keys():
    if not os.path.exists(STORE_FILE):
        return {}
    with open(STORE_FILE, "r") as f:
        return json.load(f)

def save_keys(keys):
    with open(STORE_FILE, "w") as f:
        json.dump(keys, f)
