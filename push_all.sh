#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(pwd)"
FILE="ROOM_TO_BUILD.md"
COMMIT_MSG="Docs: add ROOM_TO_BUILD and push Phase-1/Phase-2 observability changes"

echo "Working directory: $REPO_DIR"
echo

# 1) Create ROOM_TO_BUILD.md if it doesn't exist (idempotent)
if [ -f "$FILE" ]; then
  echo "$FILE already exists — skipping creation."
else
  cat > "$FILE" <<'MD'
# What's Not Done (Room to Build – ~60% There)

Full Effectors/Delivery:
- Logs deliveries but no deep integrations (e.g., actual email/calendar APIs — currently webhook proxies only).

Advanced Scaling:
- In-memory webhooks/DB (SQLite implied); no Redis/Celery for queues, no Kafka for events.

ML Polish:
- Anomalies are basic (z-score / low-confidence); need streaming ML (e.g., scikit-learn, online learners) for pattern detection and adaptive models.

SDKs:
- Raw HTTP API only — build client libraries (Python, JS, Go) with auto-generated bindings from OpenAPI.

UI/Dashboard:
- API endpoints for metrics exist, but no integrated Grafana/Streamlit visualization baked into the product UI.

Edge Features:
- No simulation/sandbox mode for safe replay testing.
- No mTLS or hardened transport for inter-service comms.
- No auto-policy learning or model-assisted policy suggestions.
- Replay/undo lacks compensating actions for side-effects; needs transactional rollback patterns for effectors.

Docs/Examples:
- README is bare; lacking step-by-step agent integration tutorials, end-to-end examples, and a HOWTO for enterprise onboarding.

---

## TL;DR
This isn't "finished" — it's a kickass prototype that safely handles end-to-end agent flows, but it needs production polish:

- Deep effectors & integrations
- Robust async queues & scaling (Redis/Celery/Kafka)
- Stronger ML & anomaly pipelines
- Polished SDKs, generated from OpenAPI
- Polished UI + dashboards
- Security hardening & simulation/replay safety
- Developer docs + examples

Rough estimate: ~60–70% done. The remaining items are mostly engineering work and productization (low-to-medium effort per item, but important for SaaS readiness).

Next brick suggestions:
- Code a full OpenAI adapter + calendar/email effector end-to-end demo.
- Add Redis + Celery for retry/queue processing.
- Auto-generate SDKs (OpenAPI -> clients) and publish Python package.
- Build a simple Streamlit/Grafana dashboard for observability.

Let's pick the first brick and spec it out / implement it next. 🚀
MD
  echo "Created $FILE"
fi

echo
# 2) Show git status and add everything
echo "Running: git status --porcelain"
git status --porcelain

echo
echo "Staging all changes..."
git add -A

# 3) Commit
# If there is nothing to commit, skip commit step
if git diff --cached --quiet; then
  echo "No changes to commit (nothing staged)."
else
  echo "Committing changes..."
  git commit -m "$COMMIT_MSG"
fi

# 4) Push
REMOTE="origin"
BRANCH="main"

# Verify remote exists
if ! git remote get-url "$REMOTE" >/dev/null 2>&1; then
  echo "Remote '$REMOTE' not found. Please add your remote (git remote add origin <url>) and re-run."
  exit 1
fi

echo "Pushing to $REMOTE $BRANCH..."

# Use GITHUB_PAT if present to avoid interactive password prompt.
if [ -n "${GITHUB_PAT:-}" ]; then
  # Rewrite remote url to include token temporarily
  REMOTE_URL=$(git remote get-url "$REMOTE")
  # Only handle https remotes
  if [[ "$REMOTE_URL" =~ ^https:// ]]; then
    AUTH_REMOTE_URL=$(echo "$REMOTE_URL" | sed -E "s#https://#https://$GITHUB_PAT@#")
    echo "Using GITHUB_PAT for authentication (token not shown). Pushing..."
    git push "$AUTH_REMOTE_URL" "$BRANCH"
    echo "Push via authenticated URL complete. Cleaning up..."
    # push via named remote for safety as well
    git push "$REMOTE" "$BRANCH"
  else
    echo "Remote URL is not HTTPS. Attempting normal git push..."
    git push "$REMOTE" "$BRANCH"
  fi
else
  # No PAT provided — try normal push (may prompt for credentials)
  git push "$REMOTE" "$BRANCH"
fi

echo
echo "Push complete. Showing recent commit:"
git --no-pager log -n 3 --oneline

echo
echo "Done. If push failed due to auth, set environment variable GITHUB_PAT and re-run:"
echo "  export GITHUB_PAT=ghp_xxx..."
echo "Then run: ./push_all.sh"
