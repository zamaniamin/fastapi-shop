from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator, model_validator

from apps.accounts.services.password import PasswordManager


class ValidatePasswordInSchema(BaseModel):
    password: str
    password_confirm: str

    @field_validator("password")
    def validate_password(cls, password: str):
        return PasswordManager.validate_password_strength(password=password, has_special_char=False)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Passwords do not match!')
        return self


# ------------------------
# --- Register Schemas ---
# ------------------------

class RegisterIn(ValidatePasswordInSchema):
    email: EmailStr

    @staticmethod
    def examples():
        examples = {
            'openapi_examples': {
                "default": {
                    "summary": "Default",
                    "value": {
                        "email": "user@example.com",
                        "password": "string",
                        "password_confirm": "string"
                    },
                },
                "with-email": {
                    "summary": "Register a new user with email verification (OTP)",
                    "description": """

> `email:"user@example.com"` The unique email address of the user. Attempting to assign the same email address to users
returns an error.
> 
>`password:"<Password1>"` The password.
> 
> `password:"<Password1>"` The password that's confirmed.  
    
For a valid password you should:
* Use numbers _**0-9**_ in the password.
* Use lowercase characters _**a-z**_ in the password.
* Use uppercase characters _**A-Z**_ in the password.
* **Optional:** Use special characters __!?@#$%^&*()+{}[]<>/__ in the password.""",
                    "value": {
                        "email": "user@example.com",
                        "password": "NewPassword123",
                        "password_confirm": "NewPassword123"
                    },
                }
            }
        }
        return examples


class RegisterOut(BaseModel):
    email: EmailStr
    message: str


class RegisterVerifyIn(BaseModel):
    email: EmailStr
    otp: str


class RegisterVerifyOut(BaseModel):
    access_token: str
    message: str


# --------------------
# --- Login Schemas ---
# --------------------
class LoginOut(BaseModel):
    access_token: str
    token_type: str


# ------------------------
# --- Password Schemas ---
# ------------------------

class PasswordResetIn(BaseModel):
    email: EmailStr


class PasswordResetOut(BaseModel):
    message: str


class PasswordResetVerifyIn(ValidatePasswordInSchema):
    email: EmailStr
    otp: str


class PasswordResetVerifyOut(BaseModel):
    message: str


class PasswordChangeIn(ValidatePasswordInSchema):
    current_password: str

    @staticmethod
    def examples():
        examples = {
            'openapi_examples': {
                "valid": {
                    "summary": "Valid Password",
                    "description": """For a valid password you should:
* Use numbers _**0-9**_ in the password.
* Use lowercase characters _**a-z**_ in the password.
* Use uppercase characters _**A-Z**_ in the password.
* **Optional:** Use special characters __!?@#$%^&*()+{}[]<>/__ in the password.
                        """,
                    "value": {
                        "current_password": "Password123",
                        "password": "NewPassword123",
                        "password_confirm": "NewPassword123"
                    },
                }
            }}
        return examples


class PasswordChangeOut(BaseModel):
    message: str


# -------------------
# --- OTP Schemas ---
# -------------------

class OTPResendIn(BaseModel):
    action: str
    email: EmailStr

    @field_validator("action")
    def validate_action(cls, value):
        allowed_actions = {"register", "reset-password", "change-email"}
        if value not in allowed_actions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid action. Allowed values are 'register', 'reset-password', 'change-email'.")
        return value

    @staticmethod
    def examples():
        examples = {
            'openapi_examples': {
                "default": {
                    "summary": "Default",
                    "description": """
- `action`: Specifies the purpose of the OTP request. Allowed values are "register", "reset-password", 
  or "change-email".
- `email`: The user's primary email address.
""",
                    "value": {
                        "action": "string",
                        "email": "user@example.com"
                    },
                },
                "register": {
                    "summary": "Resend OTP for User Registration",
                    "value": {
                        "action": "register",
                        "email": "user@example.com"
                    },
                },
                "reset-password": {
                    "summary": "Resend OTP for Password Reset",
                    "value": {
                        "action": "reset-password",
                        "email": "user@example.com"
                    },
                },
                "change-email": {
                    "summary": "Resend OTP for Email Change",
                    "value": {
                        "action": "change-email",
                        "email": "user@example.com"
                    },
                },
            }
        }
        return examples


# ----------------------------
# --- Change-Email Schemas ---
# ----------------------------

class EmailChangeIn(BaseModel):
    new_email: EmailStr


class EmailChangeOut(BaseModel):
    message: str


class EmailChangeVerifyIn(BaseModel):
    otp: str


class EmailChangeVerifyOut(BaseModel):
    message: str


# --------------------
# --- User Schemas ---
# --------------------


class UserSchema(BaseModel):
    user_id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    is_verified_email: bool
    date_joined: str
    updated_at: str
    last_login: str


class CurrentUserOut(BaseModel):
    user: UserSchema


class UpdateUserSchema(BaseModel):
    first_name: str | None
    last_name: str | None


class UpdateUserIn(BaseModel):
    user: UpdateUserSchema
