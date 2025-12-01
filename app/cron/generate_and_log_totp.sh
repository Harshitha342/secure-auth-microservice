#!/usr/bin/env bash
set -euo pipefail

DATA_FILE="/data/seed.txt"
LOG_FILE="/cron/last_code.txt"

# Check seed exists
if [ ! -f "$DATA_FILE" ]; then
  UTC_TIME="$(python - <<PY
from datetime import datetime
print(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
PY
)"
  echo "$UTC_TIME ERROR: seed file not found" >&2
  exit 1
fi

# Read seed (strip whitespace)
SEED_HEX="$(tr -d "[:space:]" < "$DATA_FILE")"

# Generate code using the correct function and ensure module is found
code=$(PYTHONPATH=/app python - <<PY
from app.totp_utils import generate_totp_code
try:
    code, _ = generate_totp_code("$SEED_HEX")
    print(code)
except Exception as e:
    print("PY_ERR:", e)
    raise
PY
)

# Validate result
if [ -z "$code" ]; then
  UTC_TIME="$(python - <<PY
from datetime import datetime
print(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
PY
)"
  echo "$UTC_TIME ERROR: no code produced (code empty)" >&2
  exit 1
fi

# Write to log with UTC timestamp
UTC_TIME="$(python - <<PY
from datetime import datetime
print(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
PY
)"
mkdir -p "$(dirname "$LOG_FILE")"
echo "$UTC_TIME 2FA Code: $code" >> "$LOG_FILE"
chmod 660 "$LOG_FILE" || true
