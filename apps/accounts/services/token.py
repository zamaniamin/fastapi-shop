from datetime import timedelta, datetime

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pyotp import TOTP

from apps.accounts.models import User, UserSecret
from apps.accounts.services.user import UserManager
from config.settings import OTP_EXPIRATION_SECONDS, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, OTP_SECRET_KEY


class JWT:
    """
    Utility class for handling JWT authentication and access tokens.

    A user's access token will be expired due to actions such as "resetting the password," "changing the password," or
    even "logging out" (logout mechanism).

    The `access-token` stored in the database serves as a flag for the logout mechanism, ensuring that when a user
    wants to log out of the system, the current token will no longer be valid.
    """

    ALGORITHM = "HS256"
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/login")

    # --- set exception ---
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"})

    @classmethod
    def create_access_token(cls, user: User) -> str:
        """
        Create a new access token for the provided user.

        Args:
            user (User): The user object for whom the access token needs to be created.

        Returns:
            str: Access token string.
        """

        # --- set data to encode ---
        to_encode = {'user_id': user.id}

        # --- set expire date ---
        to_encode.update({"exp": datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)})

        # --- generate access token ---
        access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=cls.ALGORITHM)

        cls.update_access_token(user.id, access_token)
        return access_token

    @classmethod
    async def fetch_user(cls, token: str = Depends(oauth2_scheme)) -> User:
        """
        Retrieve the user associated with the provided JWT token.

        Args:
            token (str): JWT token.

        Returns:
            User: User object if the token is valid, raises HTTPException if not.
        """

        # --- validate token ---
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[cls.ALGORITHM])
        except JWTError as e:
            raise cls.credentials_exception

        # --- validate payloads in token ---
        user_id = payload.get("user_id")
        if user_id is None:
            raise cls.credentials_exception

        # --- get user ---
        # TODO move user data to token and dont fetch them from database
        user = UserManager.get_user(user_id)
        if user is None:
            raise cls.credentials_exception

        cls.is_valid_access_token(user_id, token)

        UserManager.is_active(user)
        return user

    @classmethod
    def is_valid_access_token(cls, user_id: int, current_access_token: str):
        """
        Check if the access-token for current user is same or not.

        if not, user should be login to their account and generate new access-token.
        """

        valid_access_token = UserSecret.filter(UserSecret.user_id == user_id).first().access_token
        if current_access_token != valid_access_token:
            raise cls.credentials_exception
        return True

    @staticmethod
    def update_access_token(user_id: int, access_token: str):
        """
        Update the valid access-token for current user (a flag for logout mechanism) and older tokens will be rejected.
        """

        secret = UserSecret.filter(UserSecret.user_id == user_id).first()
        if secret:
            UserSecret.update(secret.id, access_token=access_token)
        else:
            UserSecret.create(user_id=user_id, access_token=access_token)

    @staticmethod
    def expire_current_access_token(user_id: int):
        """
        User's old access-token is expired by an actions like change or reset password.
        """
        UserSecret.update(UserSecret.filter(UserSecret.user_id == user_id).first().id, access_token=None)


class OTP:

    # TODO add to email service
    # TODO how to ensure that email is sent and delivery?

    @classmethod
    def send_otp(cls, email):
        """
        As a development OTP will be printed in the terminal
        """

        otp = cls.get_otp()
        dev_show = f"""\n\n--- Testing OTP: {otp} ---"""
        print(dev_show)

    @staticmethod
    def get_otp():
        totp = TOTP(OTP_SECRET_KEY, interval=OTP_EXPIRATION_SECONDS)
        return totp.now()

    @staticmethod
    def verify_otp(otp_code: str):
        totp = TOTP(OTP_SECRET_KEY, interval=OTP_EXPIRATION_SECONDS)
        return totp.verify(otp_code)

    @classmethod
    def regenerate_otp(cls):
        totp = TOTP(OTP_SECRET_KEY, interval=OTP_EXPIRATION_SECONDS)
        time_remaining = int(totp.interval - datetime.now().timestamp() % totp.interval)
        if time_remaining == 0:
            # TODO  resend new otp code
            return totp.now()
        else:

            # OTP has not expired, do not resend
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"OTP not expired. Resend available in {time_remaining} seconds.")

    @staticmethod
    def get_action(user_id) -> UserSecret:
        return UserSecret.filter(UserSecret.user_id == user_id).first()

    @staticmethod
    def update_action(secret_id: int, action: str):
        UserSecret.update(secret_id, otp_action=action)
