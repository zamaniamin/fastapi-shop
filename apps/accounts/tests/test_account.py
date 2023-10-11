from fastapi import status
from fastapi.testclient import TestClient

from apps.accounts.services.auth import AccountService
from apps.accounts.services.user import UserManager
from apps.core.base_test_case import BaseTestCase
from apps.main import app
from config.database import DatabaseManager


class AccountTestBase(BaseTestCase):
    register_endpoint = "/accounts/register/"
    register_verify_endpoint = "/accounts/register/verify/"

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()


class TestRegister(AccountTestBase):

    def test_register_with_email(self):
        """
        Test Register a new user with valid credentials.
        """

        payload = {
            'email': 'admin@test.com',
            'password': 'Test_12345',
            'password_confirm': 'Test_12345'
        }

        # --- request ---
        response = self.client.post(self.register_endpoint, json=payload)
        assert response.status_code == status.HTTP_201_CREATED

        # --- expected ---
        expected = response.json()
        assert expected['email'] == payload['email']
        assert expected['message'] == 'Please check your email for an OTP code to confirm your email address.'

        expected_user = UserManager.get_user(email=payload['email'])
        assert expected_user is not None
        assert expected_user.id > 0

        assert expected_user.email == payload["email"]
        assert AccountService.verify_password(payload['password'], expected_user.password) is True
        assert expected_user.otp_key is not None

        assert expected_user.first_name is None
        assert expected_user.last_name is None

        assert expected_user.verified_email is False
        assert expected_user.is_active is False
        assert expected_user.is_superuser is False

        assert expected_user.updated_at is None
        assert expected_user.last_login is None
        self.assert_datetime_format(expected_user.date_joined)

    def test_verify_registration(self):
        """
        Test activating the account after verifying the OTP code (verify email).
        """

        # --- register a user ---
        register_payload = {
            'email': 'user@test.com',
            'password': 'Test_12345'
        }
        register = AccountService.register(**register_payload)

        # --- read otp code ---
        user = UserManager.get_user(email=register_payload['email'])
        otp_key = user.otp_key
        otp = AccountService.read_otp(otp_key)

        # --- payload ---
        verify_payload = {
            'email': register_payload['email'],
            'otp': otp
        }

        # --- request ---
        response = self.client.post(self.register_verify_endpoint, json=verify_payload)
        assert response.status_code == status.HTTP_201_CREATED

        # --- expected ---
        expected = response.json()
        # assert expected['token'] == payload['email']
        assert expected['message'] == 'Your email address has been confirmed. Account activated successfully.'

        expected_user = UserManager.get_user(email=register_payload['email'])

        assert expected_user is not None
        assert expected_user.id > 0

        assert expected_user.email == register_payload['email']
        assert AccountService.verify_password(register_payload['password'], expected_user.password) is True
        assert expected_user.otp_key is None

        assert expected_user.first_name is None
        assert expected_user.last_name is None

        assert expected_user.verified_email is True
        assert expected_user.is_active is True
        assert expected_user.is_superuser is False

        self.assert_datetime_format(expected_user.last_login)
        self.assert_datetime_format(expected_user.updated_at)
        self.assert_datetime_format(expected_user.date_joined)

    # TODO test JWT token
    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    # TODO test `register` with invalid payloads.
    # TODO test `verify_registration` with invalid payloads.
    # TODO test OTP is expired
