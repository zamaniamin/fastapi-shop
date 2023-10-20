from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator, model_validator

from apps.accounts.services.auth import PasswordValidator


# ------------------------
# --- Register Schemas ---
# ------------------------

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str

    @field_validator("password")
    def validate_password(cls, password: str):
        return PasswordValidator.validate_password(password=password, has_special_char=False)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Passwords do not match!')
        return self


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


class PasswordResetVerifyIn(BaseModel):
    email: EmailStr
    otp: str
    password: str
    password_confirm: str

    @field_validator("password")
    def validate_password(cls, password: str):
        return PasswordValidator.validate_password(password=password, has_special_char=False)

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password != self.password_confirm:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Passwords do not match!')
        return self


class PasswordResetVerifyOut(BaseModel):
    message: str


# --------------------
# --- User Schemas ---
# --------------------


class UserSchema(BaseModel):
    user_id: int
    email: EmailStr
    first_name: str | None
    last_name: str | None
    verified_email: bool
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
