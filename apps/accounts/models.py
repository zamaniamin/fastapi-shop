from typing import ClassVar, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from config.database import FastModel


class User(FastModel):
    """
    User represents registered users in the application.

    Attributes:
        id (int): Unique identifier for the user.
        email (str): User's email address used for authentication and communication.
        password (str): Hashed password for user authentication.
        first_name (str, optional): User's first name. Default is None.
        last_name (str, optional): User's last name. Default is None.
        is_verified_email (bool): Flag indicating whether the user's email address has been verified.
        is_active (bool): Flag indicating whether the user's account is active.
        is_superuser (bool): Flag indicating whether the user has superuser privileges.
        role (str): User's role in the system, represented as a short string.
        date_joined (datetime): Timestamp indicating when the user account was created.
        updated_at (datetime, optional): Timestamp indicating when the user account was last updated. Default is None.
        last_login (datetime, optional): Timestamp indicating the user's last login time. Default is None.
        otp_key (ClassVar[Optional[str]]): Class variable indicating the OTP (One-Time Password) key. Default is None.
        secret (relationship): Relationship attribute linking this user to related secrets (tokens management).
        change (relationship): Relationship attribute linking this user to change requests initiated by the user.
    """

    __tablename__ = "users"

    # To solve this: (Unresolved attribute reference 'otp_key' for class 'User'). when writing codes in IDE editor
    otp_key: ClassVar[Optional[str]] = None

    id = Column(Integer, primary_key=True)
    email = Column(String(256), nullable=False, unique=True)
    password = Column(String, nullable=False)

    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)

    is_verified_email = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # TODO add unittest and check the default role is 'user', also move role to permissions table
    role = Column(String(5), default="user")

    date_joined = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    secret = relationship("UserSecret", back_populates="user", cascade="all, delete-orphan")
    change = relationship("UserChangeRequest", back_populates="user", cascade="all, delete-orphan")


class UserSecret(FastModel):
    """
    UserSecret contains temporary information for token management, including JWT and OTP tokens.

    Attributes:
        id (int): Unique identifier for the user secret entry.
        user_id (int): ID of the user associated with this secret.
        otp_key (str, optional): OTP (One-Time Password) key used for token-based authentication. Default is None.
        access_token (str, optional): Access token used for JWT authentication. Default is None.
        created_at (datetime): Timestamp indicating when this user secret entry was created.
        updated_at (datetime, optional): Timestamp indicating when this user secret entry was last updated.
        Default is None.
        user (User): Relationship attribute linking this user secret entry to the associated user.
    """

    __tablename__ = "users_secrets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    otp_key = Column(String, nullable=True)
    access_token = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    user = relationship("User", back_populates="secret")


class UserChangeRequest(FastModel):
    """
    UserChangeRequest represents change requests initiated by users, such as email or phone number changes.

    Attributes:
        id (int): Unique identifier for the change request.
        user_id (int): ID of the user who initiated the change request.
        new_email (str): New email address requested by the user.
        change_type (str): Indicates the type of change request ('email' or 'phone').
        otp_key (str): OTP (One-Time Password) key used for email or phone number verification.
        updated_at (datetime): Timestamp indicating when the change request was created.
    """

    __tablename__ = "users_changes_requests"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    new_email = Column(String(256), nullable=True)
    # new_phone = Column(String(20), nullable=True)  # Adjust the length based on your requirements
    change_type = Column(String(10), nullable=True)
    otp_key = Column(String, nullable=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="change")
