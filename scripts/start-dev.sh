#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

stop_port() {
  local port="$1"
  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${port}/tcp" >/dev/null 2>&1 || true
  fi
}

# Avoid stale dev servers serving broken module chunks.
stop_port 3000
stop_port 8000
rm -rf "$ROOT_DIR/client/node_modules/.vite"

cleanup() {
  if [[ -n "${SERVER_PID:-}" ]] && kill -0 "$SERVER_PID" 2>/dev/null; then
    kill "$SERVER_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

bash "$ROOT_DIR/scripts/start-server.sh" &
SERVER_PID=$!

cd "$ROOT_DIR"
npm --prefix client start
