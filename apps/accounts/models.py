from typing import ClassVar, Optional

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey
from sqlalchemy.orm import relationship

from config.database import FastModel


class User(FastModel):
    __tablename__ = "users"

    # To solve this: (Unresolved attribute reference 'otp_key' for class 'User'). when writing codes in IDE editor
    otp_key: ClassVar[Optional[str]] = None

    id = Column(Integer, primary_key=True)
    email = Column(String(256), nullable=False, unique=True)
    password = Column(String, nullable=False)

    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)

    # TODO rename to `is_verified_email`
    verified_email = Column(Boolean, default=False)

    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # TODO add unittest and check the default role is 'user', also move role to permissions table
    role = Column(String(5), default="user")

    date_joined = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    secret = relationship("UserSecret", back_populates="user", cascade="all, delete-orphan")


class UserSecret(FastModel):
    """
    Temporary information for tokens management (JWT and OTP)
    """

    __tablename__ = "users_secrets"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    otp_key = Column(String, nullable=True)
    is_blacklisted = Column(Boolean, default=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    user = relationship("User", back_populates="secret")
