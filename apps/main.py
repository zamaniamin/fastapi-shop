from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from config.database import DatabaseManager
from config.routers import RouterManager
from config.settings import MEDIA_DIR

# init models
DatabaseManager().create_database_tables()

# init FastAPI
app = FastAPI()
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# init routers
RouterManager(app).import_routers()
