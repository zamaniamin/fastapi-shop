import re

from pydantic import BaseModel, EmailStr, field_validator, ValidationError


class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str

    @classmethod
    @field_validator("password")
    def validate_password(cls, password: str):
        constraints = [
            len(password) >= 8,
            re.search(r'[0-9]', password) is not None,  # Has a number
            re.search(r'[A-Z]', password) is not None,  # Has an Uppercase letter
            re.search(r'[a-z]', password) is not None,  # Has a Lowercase letter
            re.search(r'[!@#$%^&*()_+{}\[\]:;"\'<>,.?/\\|]', password) is not None  # Has a special char
        ]

        if all(constraints):
            return password
        raise ValidationError(
            "Invalid password. Must contain at least 8 characters, 1 number, 1 uppercase letter, 1 lowercase "
            "letter, and 1 special character.")


class RegisterOut(BaseModel):
    email: EmailStr
    message: str


class RegisterVerifyIn(BaseModel):
    email: EmailStr
    otp: str


class RegisterVerifyOut(BaseModel):
    token: str
    message: str
