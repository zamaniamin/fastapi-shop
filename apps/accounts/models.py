from sqlalchemy import Column, Integer, String, Boolean, DateTime, func, ForeignKey, UniqueConstraint
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
        date_joined (datetime): Timestamp indicating when the user account was created.
        updated_at (datetime, optional): Timestamp indicating when the user account was last updated. Default is None.
        last_login (datetime, optional): Timestamp indicating the user's last login time. Default is None.
        user_verification (relationship): Relationship attribute linking this user to verification requests initiated by the user.
        user_role (relationship): Relationship attribute linking this user to role requests initiated by the user.
    """

    __tablename__ = "accounts_users"

    id = Column(Integer, primary_key=True)
    email = Column(String(256), nullable=False, unique=True)
    password = Column(String, nullable=False)
    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)
    is_verified_email = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    date_joined = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

    user_verification = relationship("UserVerification", back_populates="user", cascade="all, delete-orphan")
    user_role = relationship("UserRole", back_populates="user", cascade="all, delete-orphan")


class UserVerification(FastModel):
    """
    UserVerification represents change requests initiated by users, such as email or phone number changes,
    that require OTP verification.

    Attributes:
        id (int): Unique identifier for the verification request.
        user_id (int): ID of the user who initiated the verification request.
        request_type (str): Indicates the type of verification request (register /reset-password /change-email
        /change-phone).
        new_email (str): New email address requested by the user.
        new_phone (str): New phone number requested by the user.
        active_access_token (str, optional): Last valid access token used for JWT authentication. Default is None.
        created_at (datetime): Timestamp indicating when the verification request was created.
        updated_at (datetime): Timestamp indicating when the verification request was last updated.
    """

    __tablename__ = "accounts_users_verifications"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("accounts_users.id"), unique=True)

    request_type = Column(String, nullable=True)
    new_email = Column(String(256), nullable=True)
    new_phone = Column(String(256), nullable=True)
    active_access_token = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    user = relationship("User", back_populates="user_verification")


class UserRole(FastModel):
    __tablename__ = 'accounts_users_roles'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("accounts_users.id"))
    role_id = Column(Integer, ForeignKey("accounts_roles.id"))

    user = relationship("User", back_populates="user_role")
    role = relationship("Role", back_populates="user_role")

    __table_args__ = (UniqueConstraint('user_id', 'role_id'),)


class Role(FastModel):
    __tablename__ = 'accounts_roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)

    user_role = relationship('UserRole', back_populates='role', cascade="all, delete-orphan")
    role_permission = relationship('RolePermissions', back_populates='role', cascade="all, delete-orphan")


class RolePermissions(FastModel):
    __tablename__ = 'accounts_roles_permissions'

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("accounts_roles.id"))
    permission_id = Column(Integer, ForeignKey("accounts_permissions.id"))

    role = relationship("Role", back_populates="role_permission")

    __table_args__ = (UniqueConstraint('role_id', 'permission_id'),)


class Permission(FastModel):
    __tablename__ = 'accounts_permissions'

    id = Column(Integer, primary_key=True, index=True)
    content_type_id = Column(Integer, ForeignKey('fastapi_content_type.id'))
    codename = Column(String, unique=True)
    name = Column(String)

    __table_args__ = (UniqueConstraint('content_type_id', 'codename'),)
