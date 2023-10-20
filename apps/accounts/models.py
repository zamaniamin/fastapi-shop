from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from config.database import FastModel


class User(FastModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(256), nullable=False, unique=True)
    password = Column(String, nullable=False)

    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)

    # TODO refactor and move the `otp_key` to the new model `OTP` : tablename__ = "users_otp"
    otp_key = Column(String, nullable=True)

    # TODO rename to `is_verified_email`
    verified_email = Column(Boolean, default=False)

    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    # TODO add unittest and check the default role is 'user', also move role to permissions table
    role = Column(String(5), default="user")

    date_joined = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    last_login = Column(DateTime, nullable=True)

# class JWTBlacklist(FastModel):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     created_at = Column(DateTime, server_default=func.now())
#     updated_at = Column(DateTime, nullable=True, onupdate=func.now())
