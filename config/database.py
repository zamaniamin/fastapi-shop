import importlib
import os
from operator import and_
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy import create_engine, URL, MetaData
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import sessionmaker, Session, Query

from . import settings

testing = False


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
        """
        global testing  # Access the global testing flag
        db_config = settings.DATABASES.copy()
        if testing:
            db_config["database"] = "test_" + db_config["database"]

        if db_config["drivername"] == "sqlite":
            project_root = Path(__file__).parent.parent  # Assuming this is where your models are located
            db_config["database"] = os.path.join(project_root, db_config["database"])

            url = URL.create(**db_config)
            cls.engine = create_engine(url, connect_args={"check_same_thread": False})
        else:
            # for postgres
            cls.engine = create_engine(URL.create(**db_config))

        session = sessionmaker(autocommit=False, autoflush=False, bind=cls.engine)
        cls.session = session()

    @classmethod
    def create_test_database(cls):
        """
        Create and configure a test database for use in tests.
        """

        # Set the testing flag to True
        global testing
        testing = True

        # Reinitialize the DatabaseManager for testing
        cls.__init__()
        DatabaseManager.create_database_tables()

    @classmethod
    def drop_all_tables(cls):
        """
        Drop all tables in the current database.
        """
        # TODO drop tables for postgres too
        if cls.engine:
            metadata = MetaData()
            metadata.reflect(bind=cls.engine)
            for table_name, table in metadata.tables.items():
                table.drop(cls.engine)

    @classmethod
    def create_database_tables(cls):
        """
        Create database tables based on SQLAlchemy models.

        This method detects 'models.py' files in subdirectories of the 'apps'
        directory and creates corresponding database tables based on SQLAlchemy
        models defined within those files.

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

    DeclarativeBase: The SQLAlchemy declarative base class from which this model inherits.

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
    """

    # TODO update FastModel methods

    @classmethod
    def __eq__(cls, **kwargs):
        filter_conditions = [getattr(cls, key) == value for key, value in kwargs.items()]
        return and_(*filter_conditions) if filter_conditions else True

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
        except Exception:
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
            query: Query = session.query(cls).filter(condition)
        return query

    @classmethod
    def get_or_404(cls, pk):
        """
        Retrieve a record by its primary key or raise a 404 HTTPException if not found.

        Args:
            pk: The primary key value of the record to retrieve.

        Returns:
            The model instance with the specified primary key.

        Raises:
            HTTPException(404): If the record is not found.
        """
        with DatabaseManager.session as session:
            instance = session.query(cls).get(pk)
            if not instance:
                raise HTTPException(status_code=404, detail=f"{cls.__name__} not found")
        return instance

    @classmethod
    def update(cls, pk, **kwargs):
        """
        Update a record by its primary key.

        Args:
            pk: The primary key value of the record to update.
            **kwargs: Keyword arguments representing model attributes to update.

        Returns:
            The updated model instance.

        Raises:
            HTTPException(404): If the record is not found.
        """
        with DatabaseManager.session as session:

            # Retrieve the object by its primary key or raise a 404 exception
            instance = session.query(cls).get(pk)
            if not instance:
                raise HTTPException(status_code=404, detail=f"{cls.__name__} not found")

            # Update the instance attributes based on the provided kwargs
            for key, value in kwargs.items():
                setattr(instance, key, value)

            try:
                # Commit the transaction and refresh the instance
                session.commit()
                session.refresh(instance)
            except Exception:
                session.rollback()
                raise
        return instance
