from app.crypto_utils import load_private_key, decrypt_seed

priv = load_private_key("keys/student_private.pem")
enc = open("encrypted_seed.txt").read().strip()
print("Decrypted seed:", decrypt_seed(enc, priv))
