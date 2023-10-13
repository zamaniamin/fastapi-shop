from fastapi import HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator, model_validator, Field


# ------------------------
# --- Register Schemas ---
# ------------------------

class RegisterIn(BaseModel):
    email: EmailStr
    password: str
    password_confirm: str

    @field_validator("password")
    def validate_password(cls, password: str):
        if len(password) >= 8:
            return password
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail='Invalid password. Must contain at least 8 characters.')

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


# --------------------
# --- User Schemas ---
# --------------------

class CurrentUserDependsIn(BaseModel):
    email: EmailStr = Field(..., description="user email")
    password: str = Field(..., min_length=8, max_length=24, description="user password")

    # email: EmailStr


class CurrentUserOut(BaseModel):
    user_id: int
    email: EmailStr
    first_name: str
    last_name: str
    verified_email: bool
    date_joined: str
    updated_at: str
    last_login: str
