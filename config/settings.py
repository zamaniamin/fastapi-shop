from pathlib import Path

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
MEDIA_DIR = Path(__file__).resolve().parent.parent / "media"
products_list_limit = 12
