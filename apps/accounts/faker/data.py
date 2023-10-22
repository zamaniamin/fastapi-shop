from faker import Faker

from apps.accounts.services.authenticate import AccountService, PasswordManager
from apps.accounts.services.token import JWT, OTP
from apps.accounts.services.user import UserManager
from apps.core.date_time import DateTime


class BaseFakeAccount:
    fake = Faker()
    password = 'Test_1234'

    @classmethod
    def random_email(cls):
        return cls.fake.email()


class FakeAccount(BaseFakeAccount):
    """
    Populates the database with fake accounts.
    """

    @classmethod
    def register_unverified(cls):
        """
        Register a new user and get the OTP code.
        """

        # --- register a user ---
        register_payload = {
            "email": cls.random_email(),
            "password": cls.password
        }
        AccountService.register(**register_payload)

        # --- read otp code ---
        user = UserManager.get_user(email=register_payload['email'])
        otp = OTP.read_otp(user.otp_key)

        return user.email, otp

    @classmethod
    def verified_registration(cls):
        """
        Registered a new user and verified their OTP code.
        """

        # --- register a user ---
        register_payload = {
            "email": cls.random_email(),
            "password": cls.password
        }
        AccountService.register(**register_payload)

        # --- read otp code ---
        user = UserManager.get_user(email=register_payload['email'])
        otp = OTP.read_otp(user.otp_key)
        verified = AccountService.verify_registration(**{'email': user.email, 'otp': otp})
        return user.email, verified['access_token']


class FakeUser(BaseFakeAccount):

    @classmethod
    def populate_admin(cls):
        """
        Create an admin and generate an access token too.
        """

        user_data = {
            'email': cls.random_email(),
            'password': PasswordManager.hash_password(cls.password),
            'first_name': cls.fake.first_name(),
            'last_name': cls.fake.last_name(),
            'otp_key': None,
            'is_verified_email': True,
            'is_active': True,
            'is_superuser': True,
            'role': 'admin',
            'last_login': DateTime.now(),
            'updated_at': DateTime.now()
        }

        user = UserManager.new_user(**user_data)
        access_token = JWT.create_access_token(user)
        return user, access_token

    @classmethod
    def populate_user(cls):
        """
        Create a new user and generate an access token too.
        """

        user_data = {
            'email': cls.random_email(),
            'password': PasswordManager.hash_password(cls.password),
            'first_name': cls.fake.first_name(),
            'last_name': cls.fake.last_name(),
            'otp_key': None,
            'is_verified_email': True,
            'is_active': True,
            'is_superuser': False,
            'last_login': DateTime.now(),
            'updated_at': DateTime.now()
        }

        user = UserManager.new_user(**user_data)
        access_token = JWT.create_access_token(user)
        return user, access_token
