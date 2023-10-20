from datetime import timedelta, datetime

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pyotp import TOTP, random_base32

from apps.accounts.models import User
from apps.accounts.services.password import PasswordManager
from apps.accounts.services.user import UserManager
from apps.core.date_time import DateTime
from config.settings import OTP_EXPIRATION_SECONDS, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY


class AccountService:  # TODO rename file to account.py

    # ----------------
    # --- Register ---
    # ----------------

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
        data["password"] = PasswordManager.hash_password(data["password"])

        # generate an otp code
        data["otp_key"] = cls.__generate_otp_key()

        # create new user
        new_user = UserManager.new_user(**data)

        # send otp code to email
        cls.__send_otp(data["otp_key"], data['email'])

        return {
            'email': new_user.email,
            'message': 'Please check your email for an OTP code to confirm your email address.'
        }

    @classmethod
    def verify_registration(cls, **data):
        """
        Verifies user registration by validating the provided OTP code.

        For first-time users, they must validate their email address before being able to "login".
        After validation, their account will be activated, allowing them to "login" and use the app.

        During verification, the email address is validated using an OTP code. Upon successful verification,
        the user's data is updated, the account is activated, and the user can "login" to the app.
        Additionally, an `access_token` is sent to allow the user to "login" without being redirected to the login form.

        Args:
            data['email'] (str): User's email address.
            data['otp'] (str): One-Time Password (OTP) code for email verification.

        Raises:
            HTTPException: If the user is not found, the email is already verified, or an invalid OTP is provided.

        Returns:
            dict: Dictionary containing an authentication token and a success message.
        """

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

        # --- check email verified or not ---
        if user.verified_email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="This email is already verified."
            )

        # --- verify otp for this user ---
        if not cls.__verify_otp(user.otp_key, otp):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid OTP code.Please double-check and try again."
            )

        # --- Update user data and activate the account ---
        user.update(user.id, otp_key=None, verified_email=True, is_active=True, last_login=DateTime.now())

        # --- login user, generate and send authentication token to the client ---
        access_token = AuthToken.create_access_token(user)

        return {
            'access_token': access_token,
            'message': 'Your email address has been confirmed. Account activated successfully.'
        }

    # -------------
    # --- Login ---
    # -------------

    @classmethod
    def login(cls, email: str, password: str):
        """
        Login with given email and password.
        """

        user = AccountService.authenticate_user(email, password)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Inactive account.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        if not user.verified_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unverified email address.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # TODO update `last_login`

        response = {
            "access_token": AuthToken.create_access_token(user),
            "token_type": "bearer"
        }
        return response

    @classmethod
    def authenticate_user(cls, email: str, password: str):
        user = UserManager.get_user(email=email)
        if not user:
            return False
        if not PasswordManager.verify_password(password, user.password):
            return False
        return user

    # TODO add class hash password

    # ----------------
    # --- OTP Code ---
    # ----------------

    # TODO add class OTP code

    @classmethod
    def __send_otp(cls, otp_key, email):
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
    def __generate_otp_key():
        return random_base32()

    @staticmethod
    def read_otp(secret: str):
        totp = TOTP(secret, interval=OTP_EXPIRATION_SECONDS)
        return totp.now()

    @staticmethod
    def __verify_otp(secret: str, user_totp: str):
        totp = TOTP(secret, interval=OTP_EXPIRATION_SECONDS)
        return totp.verify(user_totp)

    # ----------------------
    # --- Reset Password ---
    # ----------------------

    @classmethod
    def reset_password(cls, email: str):
        """
        Reset password by user email address.
        """

        user: User | None

        user = UserManager.get_user_or_404(email=email)
        UserManager.is_active(user)
        UserManager.is_verified_email(user)

        # send otp code to email address
        user = UserManager.update_user(user.id, otp_key=cls.__generate_otp_key())
        cls.__send_otp(user.otp_key, user.email)

        return {
            'message': 'Please check your email for an OTP code to confirm the password reset request.'
        }

    @classmethod
    def verify_reset_password(cls, **data):
        """
        Verify the request for reset password.
        """
        email = data['email']
        otp = data['otp']
        password = data['password']

        user = UserManager.get_user_or_404(email=email)
        if not cls.__verify_otp(user.otp_key, otp):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid OTP code.Please double-check and try again."
            )
        # TODO if otp is valid, then add current user to token-blacklist (logout mechanism)

        # --- Update user data and activate the account ---
        # TODO check `update_at` is updated or should update its value there
        UserManager.update_user(user.id, otp_key=None, password=PasswordManager.hash_password(password))
        # TODO send an email and notice user the email is changed.
        # --- login user, generate and send authentication token to the client ---
        # access_token = AuthToken.create_access_token(user)

        return {
            # 'access_token': access_token,
            'message': 'Your password has been changed.'
        }
        # TODO (best practice) generate a new token or force to login again??


class AuthToken:
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
    async def fetch_user_by_token(cls, token: str = Depends(oauth2_scheme)):
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

        cls.is_current_user_active(user.is_active)

        return user

    @classmethod
    def is_current_user_active(cls, is_active):  # TODO convert to static method and move to usermanager
        if not is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user.")

# TODO add a sessions service to manage sections like telegram app (Devices).
