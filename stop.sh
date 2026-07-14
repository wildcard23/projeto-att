#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

if [ -f .pids/django.pid ]; then
  pid=$(cat .pids/django.pid)
  echo "Stopping Django (pid $pid)"
  kill $pid || true
  rm -f .pids/django.pid
fi

if [ -f .pids/frontend.pid ]; then
  pid=$(cat .pids/frontend.pid)
  echo "Stopping frontend (pid $pid)"
  kill $pid || true
  rm -f .pids/frontend.pid
fi

echo "Stopped services. Check logs/ for output." 
