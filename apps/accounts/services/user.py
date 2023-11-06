from fastapi import HTTPException
from starlette import status

from apps.accounts.models import User
from apps.accounts.services.password import PasswordManager
from apps.core.date_time import DateTime


class UserManager:

    @classmethod
    def create_user(cls, email: str, password: str, first_name: str | None = None, last_name: str | None = None,
                    is_verified_email: bool = False, is_active: bool = False, is_superuser: bool = False,
                    role: str = 'user', updated_at: DateTime = None, last_login: DateTime = None):
        user_data = {
            "email": email,
            "password": PasswordManager.hash_password(password),
            "first_name": first_name,
            "last_name": last_name,
            "is_verified_email": is_verified_email,
            "is_active": is_active,
            "is_superuser": is_superuser,
            "role": role,
            "updated_at": updated_at,
            "last_login": last_login
        }
        user = User.create(**user_data)
        return user

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

        return user

    @classmethod
    def update_user(cls, user_id: int, email: str | None = None, password: str | None = None,
                    first_name: str | None = None, last_name: str | None = None, is_verified_email: bool | None = None,
                    is_active: bool | None = None, is_superuser: bool | None = None, role: str | None = None,
                    last_login: DateTime | None = None):
        """
        Update a user by their ID.
        """

        user_data = {}

        if first_name is not None:
            user_data["first_name"] = first_name

        if last_name is not None:
            user_data["last_name"] = last_name

        if email is not None:
            user_data["email"] = email

        if password is not None:
            user_data["password"] = PasswordManager.hash_password(password)

        if is_verified_email is not None:
            user_data["is_verified_email"] = is_verified_email

        if is_active is not None:
            user_data["is_active"] = is_active

        if is_superuser is not None:
            user_data["is_superuser"] = is_superuser

        if role is not None:
            user_data["role"] = role

        if last_login is not None:
            user_data["last_login"] = last_login

        return User.update(user_id, **user_data)

    @classmethod
    def update_last_login(cls, user_id: int):
        """
        Update user's last login.
        """
        User.update(user_id, last_login=DateTime.now())

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
        return User.create(**user_data)

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
