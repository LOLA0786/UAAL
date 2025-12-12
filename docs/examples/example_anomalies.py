import requests

r = requests.get("http://127.0.0.1:8000/api/v1/anomalies/low_confidence")
print(r.json())
