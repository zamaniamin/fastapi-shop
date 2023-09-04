from fastapi import FastAPI
from config.database import DatabaseManager
from config.routers import RouterManager

# init models
DatabaseManager().create_database_tables()

# init FastAPI
app = FastAPI()

# init routers
RouterManager(app).import_routers()
