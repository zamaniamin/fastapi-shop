from pathlib import Path

MAX_FILE_SIZE = 5  # int number as MB
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
#  Path.cwd() / "static"
BASE_URL = "http://127.0.0.1:8000"
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"
products_list_limit = 12
