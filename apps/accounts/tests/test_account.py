import pytest
from fastapi import status
from fastapi.testclient import TestClient

from apps.accounts.faker.data import FakeAccount, FakeUser
from apps.accounts.models import UserVerification
from apps.accounts.services.authenticate import AccountService
from apps.accounts.services.password import PasswordManager
from apps.accounts.services.token import TokenService
from apps.accounts.services.user import UserManager
from apps.core.base_test_case import BaseTestCase
from apps.main import app
from config.database import DatabaseManager


class AccountTestBase(BaseTestCase):
    register_endpoint = "/accounts/register/"
    register_verify_endpoint = "/accounts/register/verify/"
    login_endpoint = "/accounts/login/"
    logout_endpoint = "/accounts/logout/"
    reset_password_endpoint = "/accounts/reset-password/"
    verify_reset_password_endpoint = "/accounts/reset-password/verify"
    otp_endpoint = "/accounts/otp/"

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
        assert PasswordManager.verify_password(payload['password'], expected_user.password) is True

        assert expected_user.first_name is None
        assert expected_user.last_name is None

        assert expected_user.is_verified_email is False
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
        email, otp = FakeAccount.register_unverified()

        # --- payload ---
        verify_payload = {
            'email': email,
            'otp': otp
        }

        # --- request ---
        response = self.client.patch(self.register_verify_endpoint, json=verify_payload)
        assert response.status_code == status.HTTP_200_OK

        # --- expected ---
        assert TokenService.validate_otp_token(otp) is True
        expected = response.json()
        assert expected['access_token'] is not None
        assert expected['message'] == 'Your email address has been confirmed. Account activated successfully.'

        expected_user = UserManager.get_user(email=email)

        assert expected_user is not None
        assert expected_user.id > 0

        assert expected_user.email == email
        assert PasswordManager.verify_password(FakeAccount.password, expected_user.password) is True

        assert expected_user.first_name is None
        assert expected_user.last_name is None

        assert expected_user.is_verified_email is True
        assert expected_user.is_active is True
        assert expected_user.is_superuser is False

        # --- expected in UserVerification ---
        change_request: UserVerification = UserVerification.filter(UserVerification.user_id == expected_user.id).first()
        assert change_request.request_type is None

        self.assert_datetime_format(expected_user.last_login)
        self.assert_datetime_format(expected_user.updated_at)
        self.assert_datetime_format(expected_user.date_joined)

    def test_register_existing_verified_email(self):
        """
        Test register a new user with an existing verified email address.
        """

        user, _ = FakeAccount.verified_registration()
        payload = {
            'email': user.email,
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
        response = self.client.patch(self.register_verify_endpoint, json=unknown_email)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_verify_registration_incorrect_otp(self):
        """
        Test verify email address with incorrect otp code or expired otp code.
        """

        # --- register a user ---
        email, otp = FakeAccount.register_unverified()

        # --- payload ---
        verify_payload = {
            'email': email,
            'otp': '123456'
        }

        # --- request ---
        response = self.client.patch(self.register_verify_endpoint, json=verify_payload)
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE

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
        response = self.client.patch(self.register_verify_endpoint, json=invalid_fields)
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


class TestLoginAccount(AccountTestBase):
    def test_successful_login(self):
        """
        Test successful login for a user.
        """

        # --- register and verify a user ---
        user, _ = FakeAccount.verified_registration()
        payload = {
            'username': user.email,
            'password': FakeAccount.password
        }

        # --- login request ---
        response = self.client.post(self.login_endpoint, data=payload)
        assert response.status_code == status.HTTP_200_OK

        # --- expected ---
        expected_login = response.json()
        assert expected_login['access_token'] is not None
        assert expected_login['token_type'] == 'bearer'

        expected_user = UserManager.get_user(email=user.email)
        self.assert_datetime_format(expected_user.last_login)

    def test_login_with_incorrect_password(self):
        """
        Test login with incorrect password.
        """

        # --- register and verify a user ---
        user, _ = FakeAccount.verified_registration()
        payload = {
            'username': user.email,
            'password': FakeAccount.password + "t"
        }

        # --- login request ---
        response = self.client.post(self.login_endpoint, data=payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_with_inactive_account(self):
        """
        Test login if user account is inactive.
        """

        # --- register and verify a user ---
        email, _ = FakeAccount.register_unverified()
        payload = {
            'username': email,
            'password': FakeAccount.password
        }

        # --- login request ---
        response = self.client.post(self.login_endpoint, data=payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_login_with_unverified_email(self):
        """
        Test login a user with unverified email address.
        """

        # --- register and verify a user ---
        email, _ = FakeAccount.register_unverified()
        payload = {
            'username': email,
            'password': FakeAccount.password
        }

        # --- login request ---
        response = self.client.post(self.login_endpoint, data=payload)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_logout(self):
        """
        Test logout from account of authenticated user.
        """

        # --- create a user ---
        user, access_token = FakeUser.populate_user()
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = self.client.post(self.logout_endpoint, headers=header)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_login_after_password_change(self):
        """
        Test login to account after password is changed.
        """

        # --- create a user ---
        user, access_token = FakeUser.populate_user()

        # --- request ---
        passwords = {
            'old_password': FakeUser.password,
            'new_password': FakeUser.password + "test"
        }

        AccountService.change_password(user=user, current_password=passwords['old_password'],
                                       password=passwords['new_password'])

        # --- login with old password ---
        old_password = {
            'username': user.email,
            'password': passwords['old_password']
        }
        response = self.client.post(self.login_endpoint, data=old_password)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # --- login with new password ---
        new_password = {
            'username': user.email,
            'password': passwords['new_password']
        }
        response = self.client.post(self.login_endpoint, data=new_password)
        assert response.status_code == status.HTTP_200_OK

    def test_login_after_password_reset(self):
        """
        Test login to account after password reset.
        """

        # --- create a user ---
        user, access_token = FakeUser.populate_user()

        # --- request ---
        new_password = FakeUser.password + "test"

        AccountService.reset_password(email=user.email)
        AccountService.verify_reset_password(email=user.email, password=new_password,
                                             otp=TokenService.create_otp_token())

        # --- login with old password ---
        old_password = {
            'username': user.email,
            'password': FakeUser.password
        }
        response = self.client.post(self.login_endpoint, data=old_password)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

        # --- login with new password ---
        new_password = {
            'username': user.email,
            'password': new_password
        }
        response = self.client.post(self.login_endpoint, data=new_password)
        assert response.status_code == status.HTTP_200_OK

    # ---------------------
    # --- Test Payloads ---
    # ---------------------

    @pytest.mark.parametrize("invalid_fields", [
        {},
        {'username': '', 'password': ''},
        {'username': ''},
        {'password': '<PASSWORD>'},
        {'username': 'valid@test.com'},
        {'username': 'any_username'}])
    def test_login_with_invalid_payloads(self, invalid_fields):
        """
        Test login to account with invalid payloads.
        """

        # --- login request ---
        response = self.client.post(self.login_endpoint, data=invalid_fields)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestResetPassword(AccountTestBase):
    def test_reset_password_with_email(self):
        """
        Test reset password by user email address.
        """

        # --- create a user ---
        user, _ = FakeUser.populate_user()

        # --- request ---
        payload = {
            'email': user.email
        }
        response = self.client.post(self.reset_password_endpoint, json=payload)
        assert response.status_code == status.HTTP_200_OK

        # --- expected ---
        expected = response.json()
        assert expected['message'] == 'Please check your email for an OTP code to confirm the password reset request.'

    def test_verify_reset_password_with_email(self):
        """
        Test verify reset password by user email address and then change their password.
        """

        # --- create a user ---
        fake_user, access_token = FakeUser.populate_user()

        # --- set a reset request ---
        AccountService.reset_password(fake_user.email)
        user = UserManager.get_user(fake_user.id)
        old_password = user.password

        # --- request ---
        payload = {
            'email': user.email,
            'otp': TokenService.create_otp_token(),
            'password': FakeUser.password,
            'password_confirm': FakeUser.password
        }
        response = self.client.patch(self.verify_reset_password_endpoint, json=payload)
        assert response.status_code == status.HTTP_200_OK

        # --- expected ---
        expected = response.json()
        assert expected['message'] == 'Your password has been changed.'

        expected_user = UserManager.get_user(user.id)
        assert PasswordManager.verify_password(payload['password'], expected_user.password) is True
        self.assert_datetime_format(expected_user.updated_at)
        self.assert_datetime_format(user.updated_at)
        # assert expected_user.updated_at != user.updated_at

        # --- test current token is set to none ---
        expected_access_token = UserVerification.filter(
            UserVerification.user_id == expected_user.id).first().active_access_token
        assert expected_access_token is None

        # --- expected in UserVerification ---
        change_request: UserVerification = UserVerification.filter(UserVerification.user_id == expected_user.id).first()
        assert change_request.request_type is None

        # --- test fetch user with old access-token ---
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        result = self.client.get("/accounts/me", headers=header)
        assert result.status_code == status.HTTP_401_UNAUTHORIZED


class TestResendOTP(AccountTestBase):
    def test_stop_resend_on_register(self):
        """
        Test stop resending otp to email address on user registration if OTP is still valid.
        """

        # --- register a user ---
        email, _ = FakeAccount.register_unverified()

        # --- request for resend an OTP ---
        payload = {
            "request_type": "register",
            "email": email
        }
        response = self.client.post(self.otp_endpoint, json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "OTP not expired. Resend available in " in response.json().get("detail")

    def test_stop_resend_on_change_email(self):
        """
        Test resending otp to email address on change email if OTP is still valid.
        """

        # --- register a user ---
        user, access_token = FakeUser.populate_user()
        new_email = FakeUser.random_email()

        # --- set a change email request ---
        AccountService.change_email(user, new_email)

        # --- request for resend an OTP ---
        payload = {
            "request_type": "change-email",
            "email": user.email
        }
        response = self.client.post(self.otp_endpoint, json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "OTP not expired. Resend available in " in response.json().get("detail")

    def test_stop_resend_on_reset_password(self):
        """
        Test resending otp to email address on reset password if OTP is still valid.
        """

        # --- register a user ---
        user, access_token = FakeUser.populate_user()

        # --- set a reset request ---
        AccountService.reset_password(user.email)

        # --- request for resend an OTP ---
        payload = {
            "request_type": "reset-password",
            "email": user.email
        }
        response = self.client.post(self.otp_endpoint, json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "OTP not expired. Resend available in " in response.json().get("detail")

    @pytest.mark.parametrize("invalid_request_type", ['register', 'reset-password'])
    def test_resend_on_change_email_invalid_request_type(self, invalid_request_type):
        """
        Test resending otp to email address on change-email with unrelated value for request type.
        """

        # --- register a user ---
        user, access_token = FakeUser.populate_user()
        new_email = FakeUser.random_email()

        # --- set a change email request ---
        AccountService.change_email(user, new_email)

        # --- request for resend an OTP ---
        payload = {
            "request_type": invalid_request_type,
            "email": user.email
        }
        response = self.client.post(self.otp_endpoint, json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json().get("detail") == "Current requested type is invalid."

    @pytest.mark.parametrize("invalid_request_type", ['register', 'change-email'])
    def test_resend_on_reset_password_invalid_request_type(self, invalid_request_type):
        """
        Test resending otp to email address on reset-password with unrelated value for request type.
        """

        # --- register a user ---
        user, access_token = FakeUser.populate_user()

        # --- set a reset request ---
        AccountService.reset_password(user.email)

        # --- request for resend an OTP ---
        payload = {
            "request_type": invalid_request_type,
            "email": user.email
        }
        response = self.client.post(self.otp_endpoint, json=payload)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json().get("detail") == "Current requested type is invalid."
    # ---------------------
    # --- Test Payloads ---
    # ---------------------

# TODO test limit user to enter otp code for 5 time. after that user should request a new code.
# TODO add issue on github for mock the expire time of tokens OTP and JWT

# TODO test OTP verification email is sent on:
#  (to ensure that email is sent and delivery)
#  1. register
#  2. change email
#  3. reset password
#  4. resend-otp (register, reset-password, change-email)

# TODO tests needs to expired time:
#  1. JWT `ACCESS_TOKEN_EXPIRE_MINUTES`
#  2. resend-otp (register, reset-password, change-email)
