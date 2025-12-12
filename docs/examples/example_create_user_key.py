import requests

r = requests.post(
    "http://127.0.0.1:8000/admin/users",
    json={
        "id": "sdk-user",
        "display_name": "SDK User",
        "role": "agent",
        "spending_limit": 1000,
    },
)
print("user:", r.json())
r2 = requests.post(
    "http://127.0.0.1:8000/admin/api-keys/create",
    json={"owner": "sdk-user", "scopes": "actions:write"},
)
print("api-key:", r2.json())
