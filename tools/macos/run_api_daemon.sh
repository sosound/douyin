#!/bin/bash
set -euo pipefail

ROOT="/Users/star/code/douyin"
PYTHON="/Users/star/.pyenv/versions/3.12.10/bin/python3"
LOG_DIR="$ROOT/.logs"

mkdir -p "$LOG_DIR"
cd "$ROOT"

export DOUK_APPLE_LIVE_IMPORT=1

exec "$PYTHON" - <<'PY'
import asyncio

from src.application.TikTokDownloader import TikTokDownloader
from src.application.main_server import APIServer
from src.custom import SERVER_HOST, SERVER_PORT


async def main():
    async with TikTokDownloader() as app:
        app.check_config()
        await app.check_settings(False)
        await app.parameter.update_params()
        await APIServer(app.parameter, app.database).run_server(
            SERVER_HOST,
            SERVER_PORT,
        )


asyncio.run(main())
PY
