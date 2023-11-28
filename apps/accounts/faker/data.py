from faker import Faker

from apps.accounts.services.authenticate import AccountService
from apps.accounts.services.token import TokenService
from apps.accounts.services.user import UserService


class BaseFakeAccount:
    fake = Faker()
    password = 'Demo_1234'

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
        user = UserService.get_user(email=register_payload['email'])

        return user.email, TokenService.create_otp_token()

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
        user = UserService.get_user(email=register_payload['email'])
        verified = AccountService.verify_registration(**{'email': user.email,
                                                         'otp': TokenService.create_otp_token()})
        return user, verified['access_token']


class FakeUser(BaseFakeAccount):

    @classmethod
    def populate_members(cls):
        """
        Create an admin and a user.
        """

        # --- admin ---
        user, access_token = FakeAccount.verified_registration()
        user_data = {
            'email': 'superuser@example.com',
            'first_name': cls.fake.first_name(),
            'last_name': cls.fake.last_name(),
            'is_superuser': True,
            'role': 'admin'
        }

        UserService.update_user(user.id, **user_data)

        # --- user ---
        user, access_token = FakeAccount.verified_registration()
        user_data = {
            'email': 'member@example.com',
            'first_name': cls.fake.first_name(),
            'last_name': cls.fake.last_name()
        }

        UserService.update_user(user.id, **user_data)

    @classmethod
    def populate_admin(cls):
        """
        Create an admin and generate an access token too.
        """

        user, access_token = FakeAccount.verified_registration()
        user_data = {
            'first_name': cls.fake.first_name(),
            'last_name': cls.fake.last_name(),
            'is_superuser': True,
            'role': 'admin'
        }

        user = UserService.update_user(user.id, **user_data)
        return user, access_token

    @classmethod
    def populate_user(cls):
        """
        Create a new user and generate an access token too.
        """

        user, access_token = FakeAccount.verified_registration()
        user_data = {
            'first_name': cls.fake.first_name(),
            'last_name': cls.fake.last_name()
        }

        user = UserService.update_user(user.id, **user_data)
        return user, access_token
