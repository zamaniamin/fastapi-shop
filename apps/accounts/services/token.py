from datetime import timedelta, datetime

from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pyotp import TOTP

from apps.accounts.models import User, UserVerification
from apps.accounts.services.user import UserManager
from config.settings import OTP_EXPIRATION_SECONDS, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, OTP_SECRET_KEY


class TokenService:
    """
    Manage "jwt-token" or "otp-token" that used for authentication.
    """

    user: User | None
    user_id: int

    ALGORITHM = "HS256"
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/login")
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                          detail="Could not validate credentials.",
                                          headers={"WWW-Authenticate": "Bearer"})

    def __init__(self, user: int | User | None = None):
        if user is not None:
            if isinstance(user, User):
                self.user = user
                self.user_id = user.id
            else:
                self.user = None
                self.user_id = user

    # --------------------
    # --- Access Token ---
    # --------------------

    """
    Utility class for handling JWT authentication and access tokens.

    A user's access token will be expired due to actions such as "resetting the password," "changing the password," or
    even "logging out" (logout mechanism).

    The `access-token` stored in the database serves as a flag for the logout mechanism, ensuring that when a user
    wants to log out of the system, the current token will no longer be valid.
    """

    def create_access_token(self) -> str:
        """
        Create a new access token for the provided user.

        Returns:
            str: Access token string.
        """

        # --- set data to encode ---
        to_encode = {'user_id': self.user_id}

        # --- set expire date ---
        to_encode.update({"exp": datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)})

        # --- generate access token ---
        access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=self.ALGORITHM)

        self.update_access_token(access_token)
        return access_token

    def update_access_token(self, token: str):
        UserVerification.update(UserVerification.filter(UserVerification.user_id == self.user_id).first().id,
                                active_access_token=token)

    def reset_access_token(self):
        UserVerification.update(UserVerification.filter(UserVerification.user_id == self.user_id).first().id,
                                active_access_token=None)

    @classmethod
    async def fetch_user(cls, token: str) -> User:
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

        UserManager.is_active(user)

        # --- validate access token ---
        active_access_token = UserVerification.filter(UserVerification.user_id == user_id).first().active_access_token
        if token != active_access_token:
            raise cls.credentials_exception

        UserManager.is_active(user)
        return user

    # -----------------
    # --- OTP Token ---
    # -----------------

    @staticmethod
    def create_otp_token():
        totp = TOTP(OTP_SECRET_KEY, interval=OTP_EXPIRATION_SECONDS)
        return totp.now()

    def request_is_register(self):
        """
        Will be used just when a new user is registered.
        """

        UserVerification.create(user_id=self.user_id, request_type='register')

    def get_new_email(self):
        _change: UserVerification = UserVerification.filter(UserVerification.user_id == self.user_id).first()
        if _change.request_type == 'change-email':
            return _change.new_email
        return False

    def request_is_change_email(self, new_email: str):
        _change = UserVerification.filter(UserVerification.user_id == self.user_id).first().id
        UserVerification.update(_change, new_email=new_email, request_type='change-email')

    def reset_is_change_email(self):
        _change = UserVerification.filter(UserVerification.user_id == self.user_id).first().id
        UserVerification.update(_change, new_email=None, request_type=None)

    def reset_otp_token_type(self):
        """
        Remove the request_type for otp token by set it to None.
        """

        _change = UserVerification.filter(UserVerification.user_id == self.user_id).first().id
        UserVerification.update(_change, request_type=None)

    @staticmethod
    def validate_otp_token(token: str):
        totp = TOTP(OTP_SECRET_KEY, interval=OTP_EXPIRATION_SECONDS)
        return totp.verify(token)

    @classmethod
    def send_otp(cls, email):
        """
        As a development OTP will be printed in the terminal
        """
        # TODO add to email service
        # TODO how to ensure that email is sent and delivery?

        otp = cls.create_otp_token()
        dev_show = f"""\n\n--- Testing OTP: {otp} ---"""
        print(dev_show)

    # @classmethod
    # def regenerate_otp(cls):
    #     totp = TOTP(OTP_SECRET_KEY, interval=OTP_EXPIRATION_SECONDS)
    #     time_remaining = int(totp.interval - datetime.now().timestamp() % totp.interval)
    #     if time_remaining == 0:
    #         # TODO  resend new otp code
    #         return totp.now()
    #     else:
    #
    #         # OTP has not expired, do not resend
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=f"OTP not expired. Resend available in {time_remaining} seconds.")
