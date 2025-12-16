import requests
import time
import sys

UAAL_URL = "http://127.0.0.1:8000"
ORG = "acme"
AGENT = "billing-agent"

def wait_for_uaal():
    print("🔌 Waiting for UAAL control plane...")
    while True:
        try:
            r = requests.get(f"{UAAL_URL}/health", timeout=2)
            if r.status_code == 200:
                print("✅ UAAL is online")
                return
        except Exception:
            pass
        time.sleep(2)

def authorize(action, amount=None):
    payload = {
        "org": ORG,
        "agent_id": AGENT,
        "action": action
    }
    if amount is not None:
        payload["amount"] = amount

    resp = requests.post(
        f"{UAAL_URL}/agent/action",
        json=payload,
        timeout=5
    )
    return resp.json()

def wait_for_approval(action, amount):
    print("⏳ Waiting for human approval...")
    while True:
        time.sleep(5)
        decision = authorize(action, amount)
        print("RETRY:", decision["status"])
        if decision["status"] == "approved":
            print("✅ Approved — executing")
            return
        if decision["status"] == "rejected":
            print("❌ Rejected permanently")
            return

def run():
    wait_for_uaal()

    print("💳 Billing Agent starting")

    print("READ:", authorize("read"))
    print("SIMULATE:", authorize("simulate", amount=12000))

    decision = authorize("execute", amount=12000)
    print("EXECUTE:", decision)

    if decision["status"] == "needs_approval":
        wait_for_approval("execute", 12000)

if __name__ == "__main__":
    run()
