from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pathlib import Path
import os

from app.config import SEED_PATH, STUDENT_PRIVKEY_PATH
from app.crypto_utils import load_private_key, decrypt_seed
from app.totp_utils import generate_totp_code, verify_totp_code
from app.storage import save_seed, load_seed

app = FastAPI(title="Secure PKI + TOTP Auth Microservice")

# Try to pre-load private key if available (not fatal)
_priv_key = None
try:
    _priv_key = load_private_key(str(STUDENT_PRIVKEY_PATH))
except Exception:
    _priv_key = None

class DecryptSeedRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

@app.post("/decrypt-seed")
def post_decrypt_seed(payload: DecryptSeedRequest):
    """
    Accepts base64 encrypted seed, decrypts using student private key,
    saves validated hex seed to SEED_PATH, returns {"status":"ok"} on success.
    On failure returns HTTP 500 with {"error": "Decryption failed"}.
    """
    global _priv_key
    # Ensure private key loaded
    if _priv_key is None:
        try:
            _priv_key = load_private_key(str(STUDENT_PRIVKEY_PATH))
        except Exception:
            raise HTTPException(status_code=500, detail={"error": "Decryption failed"})
    # Decrypt
    try:
        seed_hex = decrypt_seed(payload.encrypted_seed, _priv_key)
        # Save seed to persistent path
        save_seed(seed_hex, str(SEED_PATH))
        return {"status": "ok"}
    except Exception:
        # keep response generic per specification
        raise HTTPException(status_code=500, detail={"error": "Decryption failed"})

@app.get("/generate-2fa")
def get_generate_2fa():
    """
    Reads /data/seed.txt, generates current TOTP code and remaining seconds.
    Success: 200 {"code": "123456", "valid_for": 30}
    Error (missing seed): 500 {"error": "Seed not decrypted yet"}
    """
    try:
        seed_hex = load_seed(str(SEED_PATH))
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
    try:
        code, remaining = generate_totp_code(seed_hex)
        return {"code": code, "valid_for": remaining}
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})

@app.post("/verify-2fa")
def post_verify_2fa(payload: VerifyRequest):
    """
    Verify provided code with ±1 period tolerance.
    Missing code -> 400 {"error":"Missing code"}
    Missing seed -> 500 {"error":"Seed not decrypted yet"}
    Returns 200 {"valid": true/false}
    """
    if not payload.code:
        raise HTTPException(status_code=400, detail={"error": "Missing code"})
    try:
        seed_hex = load_seed(str(SEED_PATH))
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
    try:
        valid = verify_totp_code(seed_hex, payload.code, valid_window=1)
        return {"valid": bool(valid)}
    except Exception:
        # generic error
        raise HTTPException(status_code=500, detail={"error": "Seed not decrypted yet"})
