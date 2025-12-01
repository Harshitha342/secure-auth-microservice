#!/usr/bin/env bash
set -euo pipefail

# start cron daemon
service cron start || /etc/init.d/cron start || true

# ensure volume dirs exist
mkdir -p "${DATA_DIR}" "${CRON_DIR}" || true
chmod 0775 "${DATA_DIR}" "${CRON_DIR}" || true

# start uvicorn (replace shell with server process)
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}" --workers 1
