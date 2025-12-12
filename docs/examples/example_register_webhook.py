import requests

r = requests.post(
    "http://127.0.0.1:8000/api/v1/webhooks/register",
    json={"id": "demo-webhook", "url": "http://requestbin.net/r/xxxx"},
)
print(r.status_code, r.json())
