import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apps.accounts.faker.data import FakeAccount
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

    def test_successful_register_with_email(self):
        """
        Test Register a new user with valid credentials.
        """

        payload = {
            'email': FakeAccount.random_email(),
            'password': FakeAccount.password,
            'password_confirm': FakeAccount.password
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

    def test_successful_verify_registration(self):
        """
        Test activating the account after verifying the OTP code (verify email).
        """

        # --- register a user ---
        register_payload = {
            'email': FakeAccount.random_email(),
            'password': FakeAccount.password
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

    def test_register_existing_verified_email(self):
        """
        Test register a new user with an existing verified email address.
        """

        email, _ = FakeAccount.verified_registration()
        payload = {
            'email': email,
            'password': FakeAccount.password,
            'password_confirm': FakeAccount.password
        }
        response = self.client.post(self.register_endpoint, json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_existing_unverified_email(self):
        """
        Test register a new user with an existing unverified email address.
        """
        emai, _ = FakeAccount.register_unverified()
        payload = {
            'email': emai,
            'password': FakeAccount.password,
            'password_confirm': FakeAccount.password
        }
        response = self.client.post(self.register_endpoint, json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    @pytest.mark.parametrize("unknown_email", [
        {'email': 'valid@test.com', 'otp': ''},
        {'email': 'valid@test.com', 'otp': '123'}])
    def test_verify_register_unknown_email(self, unknown_email):
        """
        Test verify-register a new user with unknown email address.
        """

        # --- request ---
        response = self.client.post(self.register_verify_endpoint, json=unknown_email)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    @pytest.mark.parametrize("invalid_fields", [
        {},
        {'': ''},
        {'test': 'test'},
        {'email': 'invalid@testcom', 'password': 'PASSWORD'},
        {'password': 'PASSWORD', 'password_confirm': 'PASSWORD'},
        {'email': 'valid@test.com', 'password': ''},
        {'email': 'valid@test.com', 'password': 'PASSWORD_t1'},
        {'email': 'invalid@testcom', 'password': 'PASSWORD_t1', 'password_confirm': 'PASSWORD_t1'}])
    def test_register_invalid_payload_fields(self, invalid_fields):
        """
        Test register a new user with invalid payload fields.
        """

        response = self.client.post(self.register_endpoint, json=invalid_fields)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("invalid_email", [
        {'email': ''},
        {'email': 'valid@test.com'},
        {'email': '@com', 'password': 'PASSWORD_t1', 'password_confirm': 'PASSWORD_t1'},
        {'email': 'as@.com', 'password': 'PASSWORD_t1', 'password_confirm': 'PASSWORD_t1'},
        {'email': 'as@.d.com', 'password': 'PASSWORD_t1', 'password_confirm': 'PASSWORD_t1'}])
    def test_register_invalid_email(self, invalid_email):
        """
        Test register a new user with an invalid email.
        """

        response = self.client.post(self.register_endpoint, json=invalid_email)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("invalid_passwords", [
        {'password': '', 'password_confirm': ''},
        {'password': 'PASSWORD', 'password_confirm': 'PASSWORD'},
        {'password': 'PASSWORD_', 'password_confirm': 'PASSWORD_'},
        {'password': 'password_', 'password_confirm': 'password_'},
        {'password': 'password1', 'password_confirm': 'password1'},
        {'password': '_assword1', 'password_confirm': '_assword1'},
        {'password': 'Pa@1', 'password_confirm': 'Pa@1'},
        {'password': 'asdfghjk', 'password_confirm': 'asdfghjk'},
        {'password': '12345678', 'password_confirm': '12345678'},
        {'password': 'password_tt', 'password_confirm': 'password_tt'},
        {'password': 'password_Tt', 'password_confirm': 'password_Tt'},
        {'password': 'passwordTt', 'password_confirm': 'passwordTt'},
        {'password': 'Pass1', 'password_confirm': 'Pass1'},
        {'password': 'Pass1_Pass1_Pass1_Pass1_1', 'password_confirm': 'Pass1_Pass1_Pass1_Pass1_1'},
        {'password': 'PASSWORD_t1', 'password_confirm': 'PASSWORD_t2'}])
    def test_register_invalid_password(self, invalid_passwords):
        """
        Test register a new user with invalid password.
        """
        invalid_passwords['email'] = FakeAccount.random_email()
        response = self.client.post(self.register_endpoint, json=invalid_passwords)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("invalid_fields", [
        {},
        {'': ''},
        {'test': 'test'},
        {'email': ''},
        {'email': 'valid@test.com'},
        {'email': 'invalid@testcom', 'otp': '12'},
        {'email': '', 'otp': '12'}])
    def test_verify_register_invalid_payload(self, invalid_fields):
        """
        Test verify-register a new user with invalid payload.
        """

        # --- request ---
        response = self.client.post(self.register_verify_endpoint, json=invalid_fields)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.parametrize("invalid_otp", [
        {},
        {'otp': ''},
        {'otp': '11111111'},
        {'otp': 'aaaa1111'},
        {'otp': 'aaaaaaaa'}])
    def test_verify_register_invalid_otp(self, invalid_otp):
        """
        Test register a new user with invalid password.
        """
        invalid_otp['email'] = FakeAccount.register_unverified()
        response = self.client.post(self.register_endpoint, json=invalid_otp)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # TODO test verify with an expired OTP


class TestLoginAccount(BaseTestCase):
    ...
    # TODO test successful login
    # TODO test login if user is not active.
    # TODO test login if user email in unverified
    # TODO test login with incorrect password

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    # TODO test login with empty payload
    # TODO test login without email
    # TODO test login with an unknown email
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
