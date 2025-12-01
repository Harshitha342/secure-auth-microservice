import binascii
import base64
import time
from typing import Tuple
import pyotp

HEX_CHARS = set("0123456789abcdef")

def _validate_hex64(hex_seed: str) -> str:
    """Validate the input is a 64-character hex string."""
    if not isinstance(hex_seed, str):
        raise ValueError("Seed must be a string")
    s = hex_seed.strip().lower()
    if len(s) != 64:
        raise ValueError("Seed must be exactly 64 hex characters")
    if any(c not in HEX_CHARS for c in s):
        raise ValueError("Seed contains non-hex characters")
    return s

def hex64_to_base32(hex_seed: str) -> str:
    """
    Convert 64-character hex seed into base32 string without padding.
    This is required by TOTP libraries, which accept base32 secrets.
    """
    s = _validate_hex64(hex_seed)
    b = binascii.unhexlify(s)
    b32 = base64.b32encode(b).decode()
    return b32.strip("=")

def generate_totp_code(hex_seed: str) -> Tuple[str, int]:
    """
    Generate current TOTP code from hex seed.
    
    Returns:
        (code: 6-digit string, remaining_seconds: int)
    """
    b32 = hex64_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, digits=6, interval=30, digest="sha1")
    code = totp.now()
    interval = 30
    remaining = interval - (int(time.time()) % interval)
    return code, remaining

def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with ±valid_window time-step tolerance.
    """
    if not isinstance(code, str):
        return False
    if not code.isdigit() or len(code) != 6:
        return False

    b32 = hex64_to_base32(hex_seed)
    totp = pyotp.TOTP(b32, digits=6, interval=30, digest="sha1")
    return bool(totp.verify(code, valid_window=valid_window))
