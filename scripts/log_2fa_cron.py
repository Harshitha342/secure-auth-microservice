#!/usr/bin/env python3
from datetime import datetime, timezone
import sys
from pathlib import Path
from app.totp_utils import generate_totp_code

def read_seed(path="/data/seed.txt"):
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError("Seed file missing")
    data = p.read_text().strip()
    if not data:
        raise ValueError("Seed empty")
    return data

def timestamp():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

def main():
    try:
        seed = read_seed()
    except Exception as e:
        print(f"{timestamp()} ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        code, _ = generate_totp_code(seed)
    except Exception as e:
        print(f"{timestamp()} PY_ERR: {e}", file=sys.stderr)
        sys.exit(2)

    print(f"{timestamp()} 2FA Code: {code}")

if __name__ == "__main__":
    main()
