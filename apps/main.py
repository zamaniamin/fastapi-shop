from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from config.database import DatabaseManager
from config.routers import RouterManager
from config.settings import MEDIA_DIR

# -------------------
# --- Init Models ---
# -------------------

DatabaseManager().create_database_tables()

# --------------------
# --- Init FastAPI ---
# --------------------

app = FastAPI()

# ------------------
# --- Middleware ---
# ------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])

# -------------------
# --- Static File ---
# -------------------

# add static-file support, for see images by URL
app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

# --------------------
# --- Init Routers ---
# --------------------

RouterManager(app).import_routers()
