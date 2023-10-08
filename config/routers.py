import importlib
import logging
import os
from pathlib import Path


class RouterManager:
    """
    A utility class for managing FastAPI routers.

    This class detects and imports FastAPI routers from 'routers.py' files in
    the subdirectories of the 'apps' directory. It allows you to easily include
    routers in your FastAPI application.

    Attributes:
        None

    Methods:
        import_routers():
            Detects 'routers.py' files in subdirectories of the 'apps' directory
            and imports the 'router' variable from each file.

    Example Usage:
        router_manager = RouterManager()

        # Import routers from detected 'routers.py' files
        router_manager.import_routers()
    """

    def __init__(self, app):
        self.script_directory = os.path.dirname(os.path.abspath(__file__))
        self.project_root = Path(self.script_directory).parent
        self.app = app

    def import_routers(self):
        apps_directory = self.project_root / "apps"

        for app_dir in apps_directory.iterdir():
            if app_dir.is_dir():
                routers_file = app_dir / "routers.py"
                if routers_file.exists():
                    module_name = f"apps.{app_dir.name}.routers"
                    try:
                        module = importlib.import_module(module_name)
                        if hasattr(module, "router"):
                            # Add the imported router to your FastAPI application
                            self.app.include_router(module.router)
                    except ImportError as e:
                        # Log the ImportError message for debugging purposes
                        logging.error(f"Error importing module {module_name}: {e}")
