from pathlib import Path

# --------------------
# --- URL Settings ---
# --------------------

BASE_URL = "http://127.0.0.1:8000"

# --------------------
# --- JWT Settings ---
# --------------------

# Use this command to generate a key: openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# --------------------
# --- OTP Settings ---
# --------------------

OTP_SECRET_KEY = "67XKYPCGFC47RJLZAEMDM6PIRJFWOT2P"
OTP_EXPIRATION_SECONDS = 360

# -------------------------
# --- Database Settings ---
# -------------------------

# DATABASES = {
#     "drivername": "postgresql",
#     "username": "postgres",
#     "password": "admin",
#     "host": "localhost",
#     "database": "fast_store",
#     "port": 5432
# }
DATABASES = {
    "drivername": "sqlite",
    "database": "fast_store.db"
}

# ----------------------
# --- Media Settings ---
# ----------------------

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"

# int number as MB
MAX_FILE_SIZE = 5
products_list_limit = 12

# TODO add settings to limit register new user or close register
