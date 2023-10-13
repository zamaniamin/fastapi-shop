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


class TestRegisterAccount(AccountTestBase):

    def test_register_with_email(self):
        """
        Test Register a new user with valid credentials.
        """

        payload = {
            'email': 'test@test.com',
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
        AccountService.register(**register_payload)

        # --- read otp code ---
        user = UserManager.get_user(email=register_payload['email'])

        # --- payload ---
        verify_payload = {
            'email': register_payload['email'],
            'otp': AccountService.read_otp(user.otp_key)
        }

        # --- request ---
        response = self.client.post(self.register_verify_endpoint, json=verify_payload)
        assert response.status_code == status.HTTP_200_OK

        # --- expected ---
        expected = response.json()
        assert expected['access_token'] is not None
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

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    # TODO --- `register` ---

    # TODO test register with empy payload

    # TODO test register without email
    # TODO test register with invalid email
    # TODO test register with duplicate email

    # TODO test register without password
    # TODO test register without password_confirm
    # TODO test register with invalid password
    # TODO test register with passwords do not match
    # TODO test register with password `min_length`
    # TODO test register with password `max_length`
    # TODO test register with strong password

    # TODO --- `verify_registration` ---

    # TODO test verify with empty payload

    # TODO test verify without email
    # TODO test verify with invalid email
    # TODO test verify with an existing email that not related to this verification

    # TODO test verify without OTP
    # TODO test verify with invalid OTP
    # TODO test verify with an expired OTP


class TestAuthorize(BaseTestCase):
    ...


class TestLoginAccount(BaseTestCase):
    ...
    # TODO test login
    # TODO test login if user is not active.

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    # TODO test login with empty payload
    # TODO test login without email
    # TODO test login with an existing email not related to this password
    # TODO test login
    # TODO test login
    # TODO test login
    # TODO test login for `swagger Authorize`


class TestOTP(BaseTestCase):
    ...
    # TODO test OTP `OTP_EXPIRATION_SECONDS`
    # TODO test OTP is expired
    # TODO test OTP email is sent


class TestJWT(BaseTestCase):
    ...
    # TODO test JWT token
    # TODO test JWT `ACCESS_TOKEN_EXPIRE_MINUTES`
