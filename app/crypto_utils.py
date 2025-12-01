import base64
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.backends import default_backend
from pathlib import Path

def load_private_key(path: str):
    """Load RSA private key from PEM file."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Private key not found: {path}")
    data = p.read_bytes()
    return load_pem_private_key(data, password=None, backend=default_backend())

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypt base64-encoded encrypted seed using RSA/OAEP with SHA-256.
    Returns a validated 64-character hex string (lowercase).
    """

    # 1) Base64 decode
    try:
        ciphertext = base64.b64decode(encrypted_seed_b64, validate=True)
    except Exception:
        raise ValueError("Encrypted seed is not valid Base64")

    # 2) RSA OAEP decrypt (SHA256 / MGF1-SHA256 / no label)
    try:
        plaintext = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception:
        raise ValueError("RSA decryption failed")

    # 3) Decode to UTF-8
    try:
        seed_hex = plaintext.decode("utf-8").strip()
    except Exception:
        raise ValueError("Decrypted plaintext is not valid UTF-8")

    # 4) Validate: must be 64-character hex
    if len(seed_hex) != 64:
        raise ValueError("Seed must be exactly 64 hex characters")

    seed_hex = seed_hex.lower()
    if any(c not in "0123456789abcdef" for c in seed_hex):
        raise ValueError("Seed contains invalid hex characters")

    # 5) Return
    return seed_hex
