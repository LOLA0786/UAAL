import requests

# find an action_id first by listing actions
acts = requests.get("http://127.0.0.1:8000/api/v1/actions").json()
if not acts:
    print("no actions")
else:
    aid = acts[0]["action_id"]
    r = requests.post(f"http://127.0.0.1:8000/api/v1/replay/{aid}")
    print(r.json())
