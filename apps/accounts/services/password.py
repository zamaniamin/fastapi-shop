import re

from fastapi import HTTPException
from passlib.context import CryptContext
from starlette import status


class PasswordManager:
    password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    min_length: int = 8
    max_length: int = 24

    @classmethod
    def validate_password_strength(cls, password: str, has_number: bool = True, has_lowercase: bool = True,
                                   has_uppercase: bool = True, has_special_char: bool = True) -> str:
        """
        Validate a password based on the given constraints.

        Args:
            password: The password to validate.
            has_number: Use numbers (0-9) in the password.
            has_lowercase: Use lowercase characters (a-z) in the password.
            has_uppercase: Use uppercase characters (A-Z) in the password.
            has_special_char: Use special characters (!@#$%^&*()_+{}[]:;"\'<>.,.?/|) in the password.

        Returns:
            The validated password, or raises a HTTPException if the password is invalid.
        """

        cls.__validate_length(password)

        if has_number:
            cls.__validate_pattern(password,
                                   r'[0-9]', 'Invalid password. Must contain at least one number (0-9).')

        if has_uppercase:
            cls.__validate_pattern(password, r'[A-Z]',
                                   'Invalid password. Must contain at least one uppercase letter (A-Z).')

        if has_lowercase:
            cls.__validate_pattern(password, r'[a-z]',
                                   'Invalid password. Must contain at least one lowercase letter (a-z).')

        if has_special_char:
            cls.__validate_pattern(password, r'[!@#$%^&*()_+{}\[\]:;"\'<>,.?/\\|]',
                                   'Invalid password. Must contain at least one special character.')

        return password

    @classmethod
    def __validate_length(cls, password: str):
        if len(password) < cls.min_length or len(password) > cls.max_length:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f'Invalid password length. Must be between {cls.min_length} and {cls.max_length} characters.'
            )

    @classmethod
    def __validate_pattern(cls, password: str, pattern: str, message: str):
        if not re.search(pattern, password):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=message
            )

    # ---------------------
    # --- Hash Password ---
    # ---------------------

    @classmethod
    def hash_password(cls, password: str):
        return cls.password_context.hash(password)

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str):
        return cls.password_context.verify(plain_password, hashed_password)
