#!/bin/bash
set -euo pipefail

ROOT="/Users/star/code/douyin"
CONFIG="$ROOT/tools/macos/cloudflared-config.yml"
TOKEN_FILE="/Users/star/.cloudflared/macmini-tunnel.token"

mkdir -p "$ROOT/.logs"
cd "$ROOT"

if [[ ! -f "$TOKEN_FILE" ]]; then
  echo "missing tunnel token file: $TOKEN_FILE" >&2
  exit 1
fi

TOKEN="$(<"$TOKEN_FILE")"
exec /opt/homebrew/bin/cloudflared tunnel --config "$CONFIG" run --token "$TOKEN"
