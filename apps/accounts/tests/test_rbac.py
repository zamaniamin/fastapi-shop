# import pytest
# from fastapi import status
from fastapi.testclient import TestClient

from apps.accounts.faker.data import FakeUser
from apps.accounts.models import User
# from apps.accounts.models import UserVerification
# from apps.accounts.services.authenticate import AccountService
# from apps.accounts.services.password import PasswordService
# from apps.accounts.services.token import TokenService
# from apps.accounts.services.user import UserService
from apps.core.base_test_case import BaseTestCase
from apps.main import app
from config.database import DatabaseManager


# TODO add unittest for RBAC system

class RBACTestBase(BaseTestCase):
    roles_endpoint = "/accounts/roles/"

    # --- members ---
    admin: User | None = None
    # user: User | None = None
    admin_authorization = {}

    # user_authorization = {}

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

        # --- create an admin ---
        cls.admin, access_token = FakeUser.populate_superuser()
        cls.admin_authorization = {"Authorization": f"Bearer {access_token}"}

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()


class TestCreateRole(RBACTestBase):

    def test_create_role(self):
        """
        Test create a role with administrative privileges.
        """

        # set an admin user
        # add role

    # ---------------------
    # --- Test Payloads ---
    # ---------------------
