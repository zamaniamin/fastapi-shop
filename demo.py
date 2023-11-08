import asyncio

from apps.accounts.faker.data import FakeUser
from apps.products.faker.data import FakeProduct

if __name__ == "__main__":
    from fastapi import FastAPI

    from config.database import DatabaseManager
    from config.routers import RouterManager

    # init models
    DatabaseManager().create_database_tables()

    # init FastAPI
    app = FastAPI()

    # init routers
    RouterManager(app).import_routers()

    # --- Demo Users ---
    FakeUser.populate_members()

    # --- Demo Products ---
    asyncio.run(FakeProduct.populate_30_products())
