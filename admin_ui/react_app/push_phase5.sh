#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
git add .
git commit -m "Phase 5: Analytics, policy manager UI, replay/audit endpoint, React admin UI, tests"
git push origin main
