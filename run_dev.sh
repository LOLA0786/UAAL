#!/bin/bash
set -e

echo "Stopping any existing UAAL server..."
pkill -f "uvicorn app:app" || true

export PYTHONPATH="/Users/rinky/Downloads/uaal_prototype"

echo "Starting UAAL dev server..."
uvicorn app:app   --app-dir .   --host 127.0.0.1   --port 8000   --reload
