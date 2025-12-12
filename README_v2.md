UAAL Prototype v2 - Enterprise (added alongside original prototype)

Files added:
- adapters_extended.py
- db.py
- policy.py
- app_v2.py
- requirements.txt

How to run:
1. python3 -m venv venv
2. source venv/bin/activate
3. pip install -r requirements.txt
4. uvicorn app_v2:app --reload --port 8000

Admin quickstart:
1. Create admin:
   curl -X POST "http://127.0.0.1:8000/admin/users" -H "Content-Type: application/json" -d '{"id":"alice","display_name":"Alice","role":"admin","spending_limit":1000.0}'
2. Add watchlist:
   curl -X POST "http://127.0.0.1:8000/admin/watchlist" -H "Content-Type: application/json" -H "X-User-Id: alice" -d '{"type":"blacklist","field":"verb","value":"make_payment"}'
3. Send action:
   curl -X POST "http://127.0.0.1:8000/api/v1/actions" -H "Content-Type: application/json" -d '{"adapter":"openai_assistant","agent_output":{"assistant_id":"test","intent":"create_event","target":{"type":"calendar_event","attributes":{"title":"Test"}},"confidence":0.9}}'
