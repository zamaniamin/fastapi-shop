from fastapi import HTTPException
from starlette import status

from apps.accounts.models import User, UserSecret
from apps.core.date_time import DateTime


class UserManager:
    @staticmethod
    def get_user(user_id: int | None = None, email: str = None) -> User | None:
        """
        Retrieve a user based on their ID or email address.

        Args:
            user_id (int | None): The ID of the user to retrieve. Defaults to None.
            email (str | None): The email address of the user to retrieve. Defaults to None.

        Returns:
            User | None: A User object if a user is found based on the provided ID or email,
                         or None if no user is found.
        """
        if user_id:
            user = User.get(user_id)
        elif email:
            user = User.filter(User.email == email).first()
        else:
            return None

        if user is None:
            return None

        # Add the otp_key to the User object
        user.otp_key = UserSecret.filter(UserSecret.user_id == user.id).first().otp_key

        return user

    @staticmethod
    def get_user_or_404(user_id: int | None = None, email: str = None):
        user: User | None = None
        if user_id:
            user = User.get_or_404(user_id)
        elif email:
            user = User.filter(User.email == email).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found.")

        user.otp_key = UserSecret.filter(UserSecret.user_id == user.id).first().otp_key
        return user

    @classmethod
    def update_user(cls, user_id: int, **data):
        """
        Update a user by their ID.
        """

        # TODO change `last_login` to `updated_at`, check this field is auto updated or not
        # data['last_login'] = DateTime.now()

        # update secrets
        otp_key = data.pop('otp_key', None)
        if otp_key is not None:
            cls.__update_otp_key(user_id, otp_key)
        else:
            cls.__remove_otp_key(user_id)

        # return updated user data
        user = User.update(user_id, **data)
        user.otp_key = otp_key
        return user

    @staticmethod
    def to_dict(user: User):
        """
        Convert a User object to a dictionary.
        """
        _dict = {
            'user_id': user.id,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_verified_email': user.is_verified_email,
            'date_joined': DateTime.string(user.date_joined),
            'updated_at': DateTime.string(user.updated_at),
            'last_login': DateTime.string(user.last_login)
        }
        return _dict

    @classmethod
    def new_user(cls, **user_data):

        # --- get otp ---
        otp_key = user_data.pop('otp_key', None)

        # -- create a new user ---
        user = User.create(**user_data)

        # --- save a new OTP key ---
        cls.__add_otp_key(user.id, otp_key)

        return user

    @staticmethod
    def is_active(user: User):
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Inactive user.")

    @staticmethod
    def is_verified_email(user: User):
        if not user.is_verified_email:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Pleas verify your email address to continue.")
        # TODO guide user to follow the steps need to verify email address.

    @staticmethod
    def __add_otp_key(user_id: int, otp_key: str):
        UserSecret.create(user_id=user_id, otp_key=otp_key)

    @staticmethod
    def __update_otp_key(user_id: int, otp_key: str):
        secret_id = UserSecret.filter(UserSecret.user_id == user_id).first().id
        UserSecret.update(secret_id, otp_key=otp_key)

    @staticmethod
    def __remove_otp_key(user_id: int):
        secret_id = UserSecret.filter(UserSecret.user_id == user_id).first().id
        UserSecret.update(secret_id, otp_key=None)
