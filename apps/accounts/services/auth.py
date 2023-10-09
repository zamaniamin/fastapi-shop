from fastapi import HTTPException, status
from passlib.context import CryptContext
from pyotp import TOTP, random_base32

from apps.accounts.services.user import UserManager
from config.settings import OTP_EXPIRATION_SECONDS


class AccountService:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @classmethod
    def register(cls, **data):
        """
        Create a new user and send an email with OTP code.
        """

        # check if user with the given email is exist or not.
        if UserManager.get_user(email=data['email']):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email has already been taken."
            )

        # hash the password
        data["password"] = cls.hash_password(data["password"])

        # generate an otp code
        data["otp_key"] = cls.generate_otp_key()

        # create new user
        new_user = UserManager.new_user(**data)

        # send otp code to email
        cls.send_otp(data["otp_key"], data['email'])

        return {
            'email': new_user.email,
            'message': 'Please check your email for an OTP code to confirm your email address.'
        }

    @classmethod
    def verify_registration(cls, **data):
        # --- init ---
        email = data['email']
        otp = data['otp']

        # --- get user by email ---
        user = UserManager.get_user(email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        # --- verify otp for this user ---
        if not cls.verify_otp(user.otp_key, otp):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid OTP code."
            )

        user.update(user.id, otp_key=None, verified_email=True, is_active=True)

        # --- login user, generate a JWT token ---

        # set
        return {
            'token': '',
            'message': 'Your email address has been confirmed. Account activated successfully.'
        }

    @classmethod
    def send_otp(cls, otp_key, email):
        """
        As a development OTP will be printed in the terminal
        """

        # TODO how to ensure that email is sent and delivery?

        otp = cls.read_otp(otp_key)
        dev_show = f"""\n\n--- Testing OTP: {otp} ---"""
        print(dev_show)

        email_body = f"""
        Subject: Verify your email address

        Dear "{email}",
        Thank you for registering for an account on [Your Website Name].

        To verify your email address and complete your registration, please enter the following code:
        {otp}

        If you do not verify your email address within 24 hours, your account will be deleted.
        Thank you,
        The "Fast Store" Team
        """

    @classmethod
    def hash_password(cls, password: str):
        return cls.password_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str):
        return cls.password_context.verify(plain_password, hashed_password)

    @staticmethod
    def generate_otp_key():
        return random_base32()

    @staticmethod
    def read_otp(secret: str):
        totp = TOTP(secret, interval=OTP_EXPIRATION_SECONDS)
        return totp.now()

    @staticmethod
    def verify_otp(secret: str, user_totp: str):
        totp = TOTP(secret, interval=OTP_EXPIRATION_SECONDS)
        return totp.verify(user_totp)
