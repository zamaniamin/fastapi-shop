from sqlalchemy import Column, Integer, String, Boolean, DateTime, func

from config.database import FastModel


class User(FastModel):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(256), nullable=False, unique=True)
    password = Column(String, nullable=False)

    first_name = Column(String(256), nullable=True)
    last_name = Column(String(256), nullable=True)

    otp_key = Column(String, nullable=True)
    verified_email = Column(Boolean, default=False)

    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    date_joined = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
