import importlib
import os
from operator import and_
from pathlib import Path
from sqlalchemy import create_engine, URL
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import DeclarativeBase
from . import settings


class DatabaseManager:
    """
    A utility class for managing database operations using SQLAlchemy.

    The DatabaseManager simplifies the process of initializing and managing database connections, creating database
    tables based on SQLAlchemy models, and providing a session for performing database operations.

    Attributes:
        engine (Engine): The SQLAlchemy engine for the configured database.
        session (Session): The SQLAlchemy session for database interactions.

    Methods:
        __init__():
            Initializes the DatabaseManager by creating an SQLAlchemy engine and a session based on the
            specified database configuration from the 'settings' module.

        create_database_tables():
            Detects 'models.py' files in subdirectories of the 'apps' directory and creates corresponding
            database tables based on SQLAlchemy models.

    Example Usage:
        db_manager = DatabaseManager()

        # Create database tables for all detected models
        db_manager.create_database_tables()

    Example Usage2:
        DatabaseManager().create_database_tables()
    """
    engine: create_engine = None
    session: Session = None

    @classmethod
    def __init__(cls):
        """
        Initializes the DatabaseManager.

        This method creates an SQLAlchemy engine and a session based on the specified database configuration
        from the 'settings' module.
        For SQLite databases, it configures the engine for "multi-threaded" access.

        Args:
            None

        Returns:
            None
        """

        url = URL.create(**settings.DATABASES)

        # Configure the engine with or without multi-threaded support
        if settings.DATABASES["drivername"] == "sqlite":

            cls.engine = create_engine(url, connect_args={"check_same_thread": False})
        else:
            cls.engine = create_engine(url)

        # Create an SQLAlchemy session
        session = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        cls.session = session()

    @classmethod
    def create_database_tables(cls):
        """
        Create database tables based on SQLAlchemy models.

        This method detects 'models.py' files in subdirectories of the 'apps'
        directory and creates corresponding database tables based on SQLAlchemy
        models defined within those files.

        Args:
            None

        Returns:
            None
        """
        script_directory = os.path.dirname(os.path.abspath(__file__))
        project_root = Path(script_directory).parent
        apps_directory = project_root / "apps"

        for app_dir in apps_directory.iterdir():
            if app_dir.is_dir():
                models_file = app_dir / "models.py"
                if models_file.exists():
                    module_name = f"apps.{app_dir.name}.models"
                    try:
                        module = importlib.import_module(module_name)
                        if hasattr(module, "FastModel") and hasattr(module.FastModel, "metadata"):
                            module.FastModel.metadata.create_all(bind=cls.engine)
                    except ImportError:
                        pass


class FastModel(DeclarativeBase):
    """
    A base class for creating SQLAlchemy ORM models with built-in CRUD operations.

    This class provides a foundation for defining SQLAlchemy models with common
    database operations like creating, updating, and querying records. It simplifies
    database interactions while ensuring proper session management.

    Attributes:
        None

    Class Methods:
        __eq__(column, value):
            Override the equality operator to create filter conditions for querying.

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

    Args:
        DeclarativeBase: The SQLAlchemy declarative base class from which this model inherits.
    """

    @classmethod
    def __eq__(cls, **kwargs):
        filter_conditions = [getattr(cls, key) == value for key, value in kwargs.items()]
        return and_(*filter_conditions) if filter_conditions else True

    # @classmethod
    # def __eq__(cls, column, value):
    #     """
    #     Override the equality operator to create filter conditions for querying records.
    #
    #     Args:
    #         column: The SQLAlchemy column to compare.
    #         value: The value to compare against.
    #
    #     Returns:
    #         SQLAlchemy filter condition.
    #     """
    #
    #     return column == value

    @classmethod
    def create(cls, **kwargs):
        """
        Create a new instance of the model, add it to the database, and commit the transaction.

        Args:
            **kwargs: Keyword arguments representing model attributes.

        Returns:
            The newly created model instance.
        """

        instance = cls(**kwargs)
        session = DatabaseManager.session
        try:
            session.add(instance)
            session.commit()
            session.refresh(instance)
        except Exception as e:
            session.rollback()
            raise
        finally:
            session.close()
        return instance

    @classmethod
    def filter(cls, condition):
        """
        Retrieve records from the database based on a given filter condition.

        Args:
            condition: SQLAlchemy filter condition.

        Returns:
            List of model instances matching the filter condition.
        """

        with DatabaseManager.session as session:
            query = session.query(cls).filter(condition)
            result = query.all()
        return result
