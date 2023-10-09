from apps.accounts.models import User


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
            return User.get(user_id)
        elif email:
            return User.filter(User.email == email).first()
        return None

    @staticmethod
    def new_user(**user_data):
        return User.create(**user_data)
