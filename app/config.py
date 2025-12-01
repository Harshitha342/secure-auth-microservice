from pathlib import Path
import os

# Seed path: local vs Docker
DEFAULT_SEED = Path("data/seed.txt")    # for local runs
DOCKER_SEED = Path("/data/seed.txt")    # for inside container

if Path("/data").exists():
    SEED_PATH = DOCKER_SEED
else:
    SEED_PATH = DEFAULT_SEED

# Key paths: read from environment if provided, otherwise fall back to local paths
STUDENT_PRIVKEY_PATH = Path(os.environ.get("STUDENT_PRIVKEY_PATH", "keys/student_private.pem"))
INSTRUCTOR_PUBKEY_PATH = Path(os.environ.get("INSTRUCTOR_PUBKEY_PATH", "keys/instructor_public.pem"))
