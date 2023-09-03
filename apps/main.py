from fastapi import FastAPI
from config.database import DatabaseManager

# init models
DatabaseManager().create_database_tables()

# init FastAPI
app = FastAPI()
