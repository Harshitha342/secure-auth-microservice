#!/usr/bin/env bash
set -eo pipefail

DATA_FILE="/data/seed.txt"
LOG_FILE="/cron/last_code.txt"
UTC_TIME=$(date -u "+%Y-%m-%d %H:%M:%S")

if [ ! -f "$DATA_FILE" ]; then
  echo "$UTC_TIME ERROR: seed file not found" >&2
  exit 1
fi

SEED_HEX=$(tr -d '[:space:]' < "$DATA_FILE")

code=$(python3 - <<PY
from app.totp_utils import generate_totp_code_from_hex_seed
try:
    code, _ = generate_totp_code_from_hex_seed("$SEED_HEX")
    print(code)
except Exception:
    raise SystemExit(2)
PY
)

if [ $? -ne 0 ]; then
  echo "$UTC_TIME ERROR: failed to compute TOTP" >&2
  exit 1
fi

echo "$UTC_TIME 2FA Code: $code" >> "$LOG_FILE"
chmod 660 "$LOG_FILE" || true
