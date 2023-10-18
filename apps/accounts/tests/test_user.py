from fastapi import status
from fastapi.testclient import TestClient

from apps.accounts.faker.data import FakeUser
from apps.core.base_test_case import BaseTestCase
from apps.main import app
from config.database import DatabaseManager


class UserTestBase(BaseTestCase):
    user_endpoint = "/accounts/me/"
    accounts_endpoint = "/accounts/"

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()


class TestUser(UserTestBase):

    def test_successful_retrieve_me(self):
        """
        Test retrieving a current user.
        """

        # --- create user and generate token ---
        user, access_token = FakeUser.populate_user()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        # --- request to fetch user data from token ---
        response = self.client.get(self.user_endpoint, headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # --- expected user ---
        expected_user = response.json().get('user')
        assert expected_user['user_id'] == user.id
        assert expected_user['email'] == user.email
        assert expected_user['first_name'] == user.first_name
        assert expected_user['last_name'] == user.last_name
        assert expected_user['verified_email'] == user.verified_email
        self.assert_datetime_format(expected_user['date_joined'])
        self.assert_datetime_format(expected_user['updated_at'])
        self.assert_datetime_format(expected_user['last_login'])
        assert 'password' not in expected_user
        assert 'is_active' not in expected_user
        assert 'otp_key' not in expected_user

    def test_retrieve_me_protected(self):
        """
        Test endpoint is protected.
        """

        response = self.client.get(self.user_endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_single_user_403(self):
        """
        Test retrieve a single user by ID with user role. only 'admin' can access to it.
        """

        # --- create an admin with access-token ---
        user_1, access_token = FakeUser.populate_user()
        user_2, _ = FakeUser.populate_user()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        # --- request to fetch user data from token ---
        response = self.client.get(f"{self.accounts_endpoint}{user_2.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
