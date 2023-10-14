from faker import Faker

from apps.accounts.services.auth import AccountService
from apps.accounts.services.user import UserManager


class FakeAccount:
    """
    Populates the database with fake accounts.
    """

    fake = Faker()

    password = 'Test_1234'

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
        otp = AccountService.read_otp(user.otp_key)

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
        otp = AccountService.read_otp(user.otp_key)
        verified = AccountService.verify_registration(**{'email': user.email, 'otp': otp})
        return user.email, verified['access_token']

    @classmethod
    def random_email(cls):
        return cls.fake.email()
