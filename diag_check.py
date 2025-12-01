import traceback, base64, sys
from app.crypto_utils import load_private_key, decrypt_seed

path = "/tmp/encrypted_seed.txt"
try:
    enc = open(path, "r").read().strip()
except Exception as e:
    print("ERROR reading encrypted seed file:", repr(e))
    traceback.print_exc()
    sys.exit(1)

print("READ ENC LENGTH:", len(enc))
try:
    ct = base64.b64decode(enc, validate=True)
    print("DECODED CIPHERTEXT BYTES:", len(ct))
except Exception as e:
    print("BASE64 DECODE ERROR:", repr(e))

try:
    priv = load_private_key("/keys/student_private.pem")
    print("PRIVATE KEY LOADED:", type(priv))
except Exception as e:
    print("ERROR LOADING PRIVATE KEY:", repr(e))
    traceback.print_exc()
    sys.exit(2)

try:
    seed = decrypt_seed(enc, priv)
    print("DECRYPTED_SEED:", seed)
except Exception as e:
    print("DECRYPTION EXCEPTION:", repr(e))
    traceback.print_exc()
    sys.exit(3)
