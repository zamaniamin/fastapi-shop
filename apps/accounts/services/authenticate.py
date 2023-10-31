from fastapi import HTTPException, status

from apps.accounts.models import User, UserChangeRequest, UserSecret
from apps.accounts.services.password import PasswordManager
from apps.accounts.services.token import JWT, OTP
from apps.accounts.services.user import UserManager
from apps.core.date_time import DateTime


class AccountService:

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

        # create new user
        new_user = UserManager.new_user(**data)
        UserSecret.create(user_id=new_user.id, otp_action='register')

        # send otp code to email
        OTP.send_otp(data['email'])

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
        if user.is_verified_email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="This email is already verified."
            )

        # --- verify otp for this user ---
        if not OTP.verify_otp(otp):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid OTP code.Please double-check and try again."
            )

        # --- Update user data and activate the account ---
        UserManager.update_user(user.id, is_verified_email=True, is_active=True,
                                last_login=DateTime.now())

        # --- login user, generate and send authentication token to the client ---
        access_token = JWT.create_access_token(user)

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

        if not user.is_verified_email:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Unverified email address.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        UserManager.update_last_login(user.id)
        response = {
            "access_token": JWT.create_access_token(user),
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
        OTP.send_otp(user.email)  # TODO email.send_verification(user.email,OTP.get_otp())

        return {
            'message': 'Please check your email for an OTP code to confirm the password reset request.'
        }

    @classmethod
    def verify_reset_password(cls, **data):
        """
        Verify the request for reset password and if otp is valid then current access-token will expire.
        """

        email = data['email']
        otp = data['otp']
        password = data['password']

        user = UserManager.get_user_or_404(email=email)
        if not OTP.verify_otp(otp):
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="Invalid OTP code.Please double-check and try again."
            )

        # --- Update user data and activate the account ---
        UserManager.update_user(user.id, password=PasswordManager.hash_password(password))

        # --- expire old token ---
        JWT.expire_current_access_token(user.id)

        # TODO send an email and notice user the password is changed.

        return {
            'message': 'Your password has been changed.'
        }

    @classmethod
    def change_password(cls, user: User, **data):
        """
        Change password for current user, and then current access-token will be expired.
        """

        current_password = data['current_password']
        password = data['password']

        if not PasswordManager.verify_password(current_password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password.")

        # if ok, hash pass and update user and set new pass
        UserManager.update_user(user.id, password=PasswordManager.hash_password(password))

        # --- expire old token ---
        JWT.expire_current_access_token(user.id)

        return {
            'message': 'Your password has been changed.'
        }

    @classmethod
    def change_email(cls, user, new_email):
        """
        Change password for current user.
        """

        # Check if the new email address is not already associated with another user
        if UserManager.get_user(email=new_email) is None:

            existing_change_request: UserChangeRequest = UserChangeRequest.filter(
                UserChangeRequest.user_id == user.id).first()
            try:
                if existing_change_request:
                    existing_change_request.update(user.id, new_email=new_email, change_type='email')
                else:
                    UserChangeRequest.create(user_id=user.id, new_email=new_email, change_type='email')
            except Exception as e:
                # Handle specific exceptions if possible
                # TODO handle this in server log
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update/create change request: {str(e)}"
                )

            # # send otp code to new email address
            OTP.send_otp(new_email)

        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This email has already been taken."
            )

        return {
            'message': f'Please check your email "{new_email}" for an OTP code to confirm the change email request.'
        }

    @classmethod
    def verify_change_email(cls, user, otp):
        """
        Verify change password for current user.
        """

        change_request: UserChangeRequest = UserChangeRequest.filter(UserChangeRequest.user_id == user.id).first()
        change_request_id = change_request.id
        if change_request:

            if OTP.verify_otp(otp):
                if change_request.change_type == 'email':
                    # change email
                    UserManager.update_user(user.id, email=change_request.new_email)

                    # reset change-request data
                    UserChangeRequest.update(change_request_id, new_email=None, change_type=None)
            else:
                raise HTTPException(
                    status_code=status.HTTP_406_NOT_ACCEPTABLE,
                    detail="Invalid OTP code. Please double-check and try again.")
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request try it again later.")

        return {
            'message': 'Your email is changed.'
        }

    # @classmethod
    # def resend_otp(cls, **data):
    #     """
    #     Resend OTP for registration, password reset, or email change verification.
    #     """
    #
    #     email = data['email']
    #     action = data['action']
    #
    #     user = UserManager.get_user_or_404(email=email)
    #
    #     # --- validate current action ---
    #     user_secret = OTP.get_action(user.id)
    #
    #     if user_secret.otp_action != action:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=f"Invalid action requested.")
    #
    #     # --- save new OTP ---
    #     new_otp_key = OTP.regenerate_otp_key(user.otp_key)
    #     if action == 'change-email':
    #         cls.change_email(user, new_otp_key)
    #     else:
    #         ...
    #
    #     # --- resend new OTP ---
    #     OTP.send_otp(email)

# TODO add a sessions service to manage sections like telegram app (Devices).
