#!/usr/bin/env bash
# Convenience launcher for a VPS / local run.
set -e
cd "$(dirname "$0")"

if [ ! -f config.env ]; then
  echo "config.env not found. Copy config.env.sample to config.env and edit it."
  exit 1
fi

# Create/refresh a virtualenv on first run.
if [ ! -d venv ]; then
  python3 -m venv venv
  ./venv/bin/pip install --upgrade pip
  ./venv/bin/pip install -r requirements.txt
fi

exec ./venv/bin/python -m PRStreams
