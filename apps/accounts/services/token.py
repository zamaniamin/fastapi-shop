from datetime import timedelta, datetime

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pyotp import TOTP, random_base32

from apps.accounts.models import User
from apps.accounts.services.user import UserManager
from config.settings import OTP_EXPIRATION_SECONDS, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY


class JWT:
    ALGORITHM = "HS256"
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="accounts/login")

    @classmethod
    def create_access_token(cls, user: User):
        """
        Create a new access token.
        """

        # --- set data to encode ---
        to_encode = {'user_id': user.id}

        # --- set expire date ---
        to_encode.update({"exp": datetime.utcnow() + timedelta(ACCESS_TOKEN_EXPIRE_MINUTES)})

        # TODO remove current user from token-blacklist
        # --- encod data, return new access token ---
        return jwt.encode(to_encode, SECRET_KEY, algorithm=cls.ALGORITHM)

    @classmethod
    async def fetch_user(cls, token: str = Depends(oauth2_scheme)):
        """
        Get current user from JWT token.
        """

        # --- set exception ---
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"})

        # --- validate token ---
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[cls.ALGORITHM])
            user_id = payload.get("user_id")
            if user_id is None:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception

        # --- get user ---
        user = UserManager.get_user(user_id)
        if user is None:
            raise credentials_exception

        UserManager.is_active(user)

        return user


class OTP:

    @classmethod
    def send_otp(cls, otp_key, email):  # TODO add to email service
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
