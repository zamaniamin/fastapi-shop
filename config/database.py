import importlib
import os
from pathlib import Path

from sqlalchemy import create_engine, select, and_, URL
from sqlalchemy.orm import sessionmaker, declarative_base
from . import settings
from sqlalchemy.orm import DeclarativeBase

# init database
url = URL.create(**settings.DATABASES)
engine = create_engine(url)

# When working with the ORM, the session object is our main access point to the database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class FastModel(DeclarativeBase):
    """
    A base class for creating ORM models with built-in CRUD operations.

    This class provides a foundation for creating SQLAlchemy models with common
    database operations like create and filter. It allows for convenient
    interaction with the database while maintaining the session lifecycle.

    Attributes:
        None

    Class Methods:
        __eq__(column, value):
            Override the equality operator to create filter conditions.

        create(**kwargs):
            Create a new instance of the model, add it to the database, and commit the transaction.

        filter(condition):
            Retrieve records from the database based on a given filter condition.

    Example Usage:
        class Product(FastModel):
            ...

        # Create a new product
        new_product = Product.create(product_name="Example Product", ...)

        # Filter products based on a condition
        active_products = Product.filter(Product.status == "active")
    """

    @classmethod
    def __eq__(cls, column, value):
        # Override the equality operator to create filter conditions
        return column == value

    @classmethod
    def create(cls, **kwargs):
        instance = cls(**kwargs)
        session = SessionLocal()
        try:
            # instance = cls(**kwargs)
            session.add(instance)
            session.commit()
            session.refresh(instance)
        except:
            session.rollback()
            raise
        finally:
            session.close()
        return instance

    @classmethod
    def filter(cls, condition):
        Session = sessionmaker(bind=engine)

        result = None
        with Session() as session:
            query = session.query(cls).filter(condition)
            result = query.all()
        return result


class DatabaseManager:
    """
    A utility class for managing database operations.

    This class simplifies the process of creating database tables by automatically
    detecting and creating tables based on the presence of 'models.py' files in
    the subdirectories of the 'apps' directory. It is designed to be used in
    conjunction with SQLAlchemy and Alembic for database management.

    Attributes:
        None

    Methods:
        create_database_tables():
            Detects 'models.py' files in subdirectories of the 'apps' directory
            and creates corresponding database tables based on SQLAlchemy models.

    Example Usage:
        db_manager = DatabaseManager()

        # Create database tables for all detected models
        db_manager.create_database_tables()
    """

    def __init__(self):
        self.script_directory = os.path.dirname(os.path.abspath(__file__))
        self.project_root = Path(self.script_directory).parent

    def create_database_tables(self):
        apps_directory = self.project_root / "apps"

        for app_dir in apps_directory.iterdir():
            if app_dir.is_dir():
                models_file = app_dir / "models.py"
                if models_file.exists():
                    module_name = f"apps.{app_dir.name}.models"
                    try:
                        module = importlib.import_module(module_name)
                        if hasattr(module, "FastModel") and hasattr(module.FastModel, "metadata"):
                            module.FastModel.metadata.create_all(bind=engine)
                    except ImportError:
                        pass
