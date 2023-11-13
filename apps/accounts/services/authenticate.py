from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from apps.accounts.models import User
from apps.accounts.services.password import PasswordManager
from apps.accounts.services.token import TokenService
from apps.accounts.services.user import UserManager
from apps.core.date_time import DateTime
from apps.core.services.email_manager import EmailService


class AccountService:

    @classmethod
    async def current_user(cls, token: str = Depends(OAuth2PasswordBearer(tokenUrl="accounts/login"))) -> User:
        user = await TokenService.fetch_user(token)
        return user

    # ----------------
    # --- Register ---
    # ----------------

    @classmethod
    def register(cls, email: str, password: str):
        """
        Create a new user and send an email with OTP code.
        """

        # check if user with the given email is exist or not.
        if UserManager.get_user(email=email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email has already been taken."
            )

        new_user = UserManager.create_user(email=email, password=password)
        TokenService(new_user.id).request_is_register()
        EmailService.register_send_verification_email(new_user.email)

        return {'email': new_user.email,
                'message': 'Please check your email for an OTP code to confirm your email address.'}

    @classmethod
    def verify_registration(cls, email: str, otp: str):
        """
        Verifies user registration by validating the provided OTP code.

        For first-time users, they must validate their email address before being able to "login".
        After validation, their account will be activated, allowing them to "login" and use the app.

        During verification, the email address is validated using an OTP code. Upon successful verification,
        the user's data is updated, the account is activated, and the user can "login" to the app.
        Additionally, an `access_token` is sent to allow the user to "login" without being redirected to the login form.

        Args:
            email (str): User's email address.
            otp (str): One-Time Password (OTP) code for email verification.

        Raises:
            HTTPException: If the user is not found, the email is already verified, or an invalid OTP is provided.

        Returns:
            dict: Dictionary containing an authentication token and a success message.
        """

        # --- get user by email ---
        user = UserManager.get_user(email=email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found."
            )

        # --- check email verified or not ---
        if user.is_verified_email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="This email is already verified."
            )

        # --- validate otp_token for this user ---
        token = TokenService(user=user)

        if not token.validate_otp_token(otp):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid OTP code. Please double-check and try again."
            )

        # --- Update user data and activate the account ---
        UserManager.update_user(user.id, is_verified_email=True, is_active=True, last_login=DateTime.now())

        token.reset_otp_token_type()

        return {'access_token': token.create_access_token(),
                'message': 'Your email address has been confirmed. Account activated successfully.'}

    # -------------
    # --- Login ---
    # -------------

    @classmethod
    def login(cls, email: str, password: str):
        """
        Login with given email and password.
        """

        user = cls.authenticate_user(email, password)
        token: TokenService = TokenService(user)

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

        if not user.is_verified_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unverified email address.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        UserManager.update_last_login(user.id)
        return {"access_token": token.create_access_token(), "token_type": "bearer"}

    @classmethod
    def authenticate_user(cls, email: str, password: str):
        user = UserManager.get_user(email=email)
        if not user:
            return False
        if not PasswordManager.verify_password(password, user.password):
            return False
        return user

    # ----------------------
    # --- Reset Password ---
    # ----------------------

    @classmethod
    def reset_password(cls, email: str):
        """
        Reset password by user email address.
        """
        # TODO stop resend email until current otp not expired
        user: User | None

        user = UserManager.get_user_or_404(email=email)
        UserManager.is_active(user)
        UserManager.is_verified_email(user)

        token = TokenService(user.id)
        token.reset_is_reset_password()

        EmailService.reset_password_send_verification_email(user.email)

        return {'message': 'Please check your email for an OTP code to confirm the password reset request.'}

    @classmethod
    def verify_reset_password(cls, email: str, password: str, otp: str):
        """
        Verify the request for reset password and if otp is valid then current access-token will expire.
        """

        user = UserManager.get_user_or_404(email=email)
        token = TokenService(user.id)

        if not token.validate_otp_token(otp):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid OTP code.Please double-check and try again."
            )

        UserManager.update_user(user.id, password=password)
        token.reset_otp_token_type()
        token.reset_access_token()
        # TODO send an email and notice user the password is changed.

        return {'message': 'Your password has been changed.'}

    @classmethod
    def change_password(cls, user: User, current_password: str, password: str):
        """
        Change password for current user, and then current access-token will be expired.
        """

        if not PasswordManager.verify_password(current_password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password.")

        UserManager.update_user(user.id, password=password)
        TokenService(user.id).reset_access_token()

        return {'message': 'Your password has been changed.'}

    @classmethod
    def change_email(cls, user, new_email):
        """
        Change password for current user.
        """

        # Check if the new email address is not already associated with another user
        if UserManager.get_user(email=new_email) is None:

            TokenService(user.id).request_is_change_email(new_email)
            EmailService.change_email_send_verification_email(new_email)

        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This email has already been taken.")

        return {
            'message': f'Please check your email "{new_email}" for an OTP code to confirm the change email request.'}

    @classmethod
    def verify_change_email(cls, user, otp):
        """
        Verify change password for current user.
        """

        token = TokenService(user.id)

        if token.validate_otp_token(otp):
            new_email = token.get_new_email()

            if new_email:
                UserManager.update_user(user.id, email=new_email)
                token.reset_is_change_email()
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid request for email verification.")
        else:
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid OTP code. Please double-check and try again.")

        return {'message': 'Your email is changed.'}

    @classmethod
    def resend_otp(cls, request_type: str, email: str):
        """
        Resend OTP for registration, password reset, or email change verification.
        """

        user = UserManager.get_user_or_404(email=email)
        token = TokenService(user.id)

        # --- validate current request type ---
        current_request_type = token.get_otp_request_type()
        if current_request_type != request_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Current requested type is invalid.")

        if current_request_type == 'change_email':
            email = token.get_new_email()

        # --- resend new OTP ---
        token.check_time_remaining()
        match request_type:
            case 'register':
                EmailService.register_send_verification_email(email)
            case 'change-email':
                EmailService.change_email_send_verification_email(email)
            case 'reset-password':
                EmailService.reset_password_send_verification_email(email)

    @classmethod
    def logout(cls, current_user):
        TokenService(current_user).reset_access_token()

# TODO add a sessions service to manage sections like telegram app (Devices).
