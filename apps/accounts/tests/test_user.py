from fastapi import status
from fastapi.testclient import TestClient

from apps.accounts.faker.data import FakeUser
from apps.accounts.models import UserVerification
from apps.accounts.services.authenticate import AccountService
from apps.accounts.services.password import PasswordManager
from apps.accounts.services.token import TokenService
from apps.accounts.services.user import UserManager
from apps.core.base_test_case import BaseTestCase
from apps.main import app
from config.database import DatabaseManager


class UserTestBase(BaseTestCase):
    current_user_endpoint = "/accounts/me/"
    change_password_endpoint = "/accounts/me/password/"
    change_email_endpoint = "/accounts/me/email/"
    verify_change_email_endpoint = "/accounts/me/email/verify/"
    accounts_endpoint = "/accounts/"

    @classmethod
    def setup_class(cls):
        cls.client = TestClient(app)
        DatabaseManager.create_test_database()

    @classmethod
    def teardown_class(cls):
        DatabaseManager.drop_all_tables()


class TestRetrieveUser(UserTestBase):

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
        response = self.client.get(self.current_user_endpoint, headers=headers)
        assert response.status_code == status.HTTP_200_OK

        # --- expected user ---
        expected_user = response.json().get('user')
        assert expected_user['user_id'] == user.id
        assert expected_user['email'] == user.email
        assert expected_user['first_name'] == user.first_name
        assert expected_user['last_name'] == user.last_name
        assert expected_user['is_verified_email'] == user.is_verified_email
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

        response = self.client.get(self.current_user_endpoint)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_retrieve_single_user(self):
        """
        Test retrieve a single user by ID with admin role. only 'admin' can access to it.
        """

        # --- create an admin with access-token ---
        admin, access_token = FakeUser.populate_admin()
        user, _ = FakeUser.populate_user()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        # --- request to fetch user data from token ---
        response = self.client.get(f"{self.accounts_endpoint}{user.id}", headers=headers)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_single_user_403(self):
        """
        Test retrieve a single user by ID with user role. only 'admin' can access to it.
        """

        # --- create user with access-token ---
        user_1, access_token = FakeUser.populate_user()
        user_2, _ = FakeUser.populate_user()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        # --- request to fetch user data from token ---
        response = self.client.get(f"{self.accounts_endpoint}{user_2.id}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # ---------------------
    # --- Test Payloads ---
    # ---------------------


class TestUpdateUser(UserTestBase):
    def test_update_current_user(self):
        """
        Test update the current user with "user" role.
        """

        # --- create user ---
        user, access_token = FakeUser.populate_user()
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        payload = {
            'first_name': FakeUser.fake.first_name(),
            'last_name': FakeUser.fake.last_name()
        }

        # --- request ---
        response = self.client.put(self.current_user_endpoint, headers=headers, json=payload)
        assert response.status_code == status.HTTP_200_OK

        # --- expected ---
        expected_user = response.json().get('user')
        assert expected_user['first_name'] == payload['first_name']
        assert expected_user['last_name'] == payload['last_name']
        self.assert_datetime_format(expected_user['updated_at'])

    # TODO update current admin

    # ---------------------
    # --- Test Payloads ---
    # ---------------------


class TestChanges(UserTestBase):

    def test_change_password(self):
        """
        Test change password by current user.
        """

        # --- create a user ---
        user, access_token = FakeUser.populate_user()
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        # --- request ---
        payload = {
            'current_password': FakeUser.password,
            'password': FakeUser.password + "test",
            'password_confirm': FakeUser.password + "test"
        }
        response = self.client.patch(self.change_password_endpoint, headers=header, json=payload)
        assert response.status_code == status.HTTP_200_OK

        # --- expected ---
        expected = response.json()
        assert expected['message'] == 'Your password has been changed.'

        # --- expected user data, ensure other info wasn't changed ---
        expected_user = UserManager.get_user(user.id)
        assert PasswordManager.verify_password(payload['password'], expected_user.password) is True
        assert expected_user.email == user.email
        assert expected_user.is_verified_email is True
        assert expected_user.role == user.role
        assert expected_user.first_name == user.first_name
        assert expected_user.last_name == user.last_name
        # assert expected_user.updated_at != user.updated_at
        assert expected_user.date_joined == user.date_joined
        assert expected_user.last_login == user.last_login
        self.assert_datetime_format(expected_user.date_joined)
        self.assert_datetime_format(expected_user.updated_at)
        self.assert_datetime_format(expected_user.last_login)

        # --- test current token is set to none ---
        expected_access_token = UserVerification.filter(
            UserVerification.user_id == expected_user.id).first().active_access_token
        assert expected_access_token is None

        # --- test fetch user with old access-token ---
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        result = self.client.get(self.current_user_endpoint, headers=header)
        assert result.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_email(self):
        """
        Test change the email of the current user.
        """

        # --- create a user ---
        user, access_token = FakeUser.populate_user()

        # --- request ---
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {'new_email': FakeUser.random_email()}

        response = self.client.post(self.change_email_endpoint, headers=header, json=payload)
        assert response.status_code == status.HTTP_200_OK

        # --- expected change request ---
        change_request: UserVerification = UserVerification.filter(UserVerification.user_id == user.id).first()
        assert change_request.new_email == payload["new_email"]
        assert change_request.request_type == 'change-email'

        # --- expected response ---
        expected = response.json()
        assert expected['message'] == (f'Please check your email \"{payload["new_email"]}\" for an OTP code to'
                                       f' confirm the change email request.')

    def test_verify_email_change_request(self):
        """
        Test verify the change email of the current.
        """

        # --- create a user ---
        user, access_token = FakeUser.populate_user()
        new_email = FakeUser.random_email()

        # --- set a change email request ---
        AccountService.change_email(user, new_email)

        # --- request ---
        header = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            'otp': TokenService.create_otp_token(),
        }

        response = self.client.patch(self.verify_change_email_endpoint, headers=header, json=payload)
        assert response.status_code == status.HTTP_200_OK

        # --- expected response ---
        expected = response.json()
        assert expected['message'] == 'Your email is changed.'

        # --- expected user data, ensure other info wasn't changed ---
        expected_user = UserManager.get_user(user.id)
        assert expected_user.email == new_email
        assert expected_user.is_verified_email is True
        assert expected_user.role == user.role
        assert expected_user.first_name == user.first_name
        assert expected_user.last_name == user.last_name
        assert expected_user.password == user.password
        # assert expected_user.updated_at != user.updated_at
        assert expected_user.date_joined == user.date_joined
        assert expected_user.last_login == user.last_login
        self.assert_datetime_format(expected_user.date_joined)
        self.assert_datetime_format(expected_user.updated_at)
        self.assert_datetime_format(expected_user.last_login)

        # --- expected in UserVerification ---
        change_request: UserVerification = UserVerification.filter(UserVerification.user_id == user.id).first()
        assert change_request.new_email is None
        assert change_request.request_type is None

        # --- test current token is valid ---
        expected_access_token = UserVerification.filter(
            UserVerification.user_id == expected_user.id).first().active_access_token
        assert expected_access_token == access_token

        # ---------------------
        # --- Test Payloads ---
        # ---------------------
