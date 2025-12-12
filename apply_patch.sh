#!/usr/bin/env bash
set -e
FILE="app_v2.py"
if [ ! -f "$FILE" ]; then
  echo "app_v2.py not found in current directory"
  exit 1
fi
echo "Applying safe replacements to $FILE"

py - <<'PY' 2>/dev/null || python3 - <<'PY'
import io,sys,re
fname = "app_v2.py"
s = open(fname,"r",encoding="utf-8").read()

replacements = [
    (r"from fastapi import FastAPI, HTTPException, Request, Header",
     "from fastapi import FastAPI, HTTPException, Request, Header, Depends"),
    (r"(import adapters_extended as adapters)",
     "\\1\\nimport middleware_auth\\nimport middleware_rbac"),
    (r"async def receive_action\\(payload: ReceiveAction, x_user_id: Optional\\[str\\] = Header\\(None\\)\\):",
     "async def receive_action(payload: ReceiveAction, current_user: dict = Depends(middleware_auth.get_current_user)):"),

    (r"async def approve_action\\(action_id: str, x_user_id: Optional\\[str\\] = Header\\(None\\)\\):",
     "async def approve_action(action_id: str, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role(\"approver\"))):"),

    (r"async def reject_action\\(action_id: str, x_user_id: Optional\\[str\\] = Header\\(None\\)\\):",
     "async def reject_action(action_id: str, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role(\"approver\"))):"),

    (r"def create_user\\(u: CreateUser\\):",
     "def create_user(u: CreateUser, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role(\"admin\"))):"),

    (r"def add_watchlist\\(entry: WatchlistEntry, x_user_id: Optional\\[str\\] = Header\\(None\\)\\):",
     "def add_watchlist(entry: WatchlistEntry, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role(\"admin\"))):"),

    (r"async def register_webhook\\(req: Request, x_user_id: Optional\\[str\\] = Header\\(None\\)\\):",
     "async def register_webhook(req: Request, current_user: dict = Depends(middleware_auth.get_current_user)):"),

    (r"def admin_api_key_create\\(payload: dict\\):",
     "def admin_api_key_create(payload: dict, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role(\"admin\"))):"),

    (r"def admin_api_key_verify\\(payload: dict\\):",
     "def admin_api_key_verify(payload: dict, current_user: dict = Depends(middleware_auth.get_current_user), _=Depends(middleware_rbac.require_role(\"admin\"))):"),
]

for pat, rep in replacements:
    new = re.sub(pat, rep, s)
    if new != s:
        print("Applied replacement for pattern:", pat)
    s = new

open(fname,"w",encoding="utf-8").write(s)
print("Patching complete.")
PY

chmod +x apply_patch.sh
echo "Run ./apply_patch.sh to apply changes to app_v2.py"

