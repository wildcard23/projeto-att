#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

mkdir -p .pids logs

# Backend: venv, install, migrate, run
if [ ! -d ".venv" ]; then
  python -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
nohup python manage.py runserver 0.0.0.0:8000 > logs/django.log 2>&1 &
echo $! > .pids/django.pid

# Frontend: install if needed and run
cd frontend
if [ ! -d "node_modules" ]; then
  npm ci
fi
nohup npm start > ../logs/frontend.log 2>&1 &
echo $! > ../.pids/frontend.pid

echo "Started backend (pid $(cat .pids/django.pid)) and frontend (pid $(cat .pids/frontend.pid))."
