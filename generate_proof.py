#!/usr/bin/env python3
"""
generate_proof.py

Generates commit-proof:
 - reads HEAD commit hash (40-char hex)
 - signs the ASCII commit hash using RSA-PSS (SHA-256, MGF1(SHA256), salt=PSS.MAX_LENGTH)
 - encrypts the signature with instructor public key using RSA/OAEP-SHA-256
 - outputs Commit Hash and Encrypted Signature (base64, single-line)
"""

import subprocess
import sys
import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend


STUDENT_PRIVKEY_PATH = Path("keys/student_private.pem")
INSTRUCTOR_PUBKEY_PATH = Path("keys/instructor_public.pem")


def load_private_key(path: Path):
    data = path.read_bytes()
    return serialization.load_pem_private_key(data, password=None, backend=default_backend())


def load_public_key(path: Path):
    data = path.read_bytes()
    return serialization.load_pem_public_key(data, backend=default_backend())


def sign_message(message: str, private_key) -> bytes:
    msg_bytes = message.encode("utf-8")
    return private_key.sign(
        msg_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )


def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    return public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )


def get_head_commit_hash() -> str:
    out = subprocess.check_output(["git", "rev-parse", "HEAD"])
    commit_hash = out.decode().strip()
    if len(commit_hash) != 40:
        raise ValueError("Invalid commit hash length")
    return commit_hash


def main():
    commit_hash = get_head_commit_hash()

    priv = load_private_key(STUDENT_PRIVKEY_PATH)
    instr_pub = load_public_key(INSTRUCTOR_PUBKEY_PATH)

    signature = sign_message(commit_hash, priv)
    encrypted = encrypt_with_public_key(signature, instr_pub)
    encrypted_b64 = base64.b64encode(encrypted).decode()

    result = {
        "commit_hash": commit_hash,
        "encrypted_signature_b64": encrypted_b64
    }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
