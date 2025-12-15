#!/bin/bash
set -e

echo "Starting UAAL demo server (stable mode)..."

uvicorn app:app   --host 127.0.0.1   --port 8000
