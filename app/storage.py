import os
from pathlib import Path

def save_seed(seed_hex: str, path: str):
    """
    Save the seed (64-char hex string) to the given path.
    Ensure the directory exists.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(seed_hex.strip())

    # Set file permission (best effort)
    try:
        os.chmod(p, 0o600)
    except Exception:
        pass

def load_seed(path: str) -> str:
    """
    Load the hex seed from disk.
    Raise FileNotFoundError if missing.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Seed file not found: {path}")

    seed = p.read_text().strip()
    return seed
