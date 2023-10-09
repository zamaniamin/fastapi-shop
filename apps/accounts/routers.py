from fastapi import APIRouter, status

from apps.accounts import schemas
from apps.accounts.services.auth import AccountService

router = APIRouter(
    prefix="/accounts",
    tags=["Authentication"]
)


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.RegisterOut,
    summary='Register a new user',
    description='Register a new user by email.')
async def register(payload: schemas.RegisterIn):
    return AccountService.register(**payload.model_dump(exclude={"password_confirm"}))


@router.post(
    "/register/verify",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.RegisterVerifyOut,
    summary='Verify user registration',
    description='Verify a new user registration by confirming the provided OTP.')
async def verify_registration(payload: schemas.RegisterVerifyIn):
    return AccountService.verify_registration(**payload.model_dump())


# =====================================

# to get a string like this run:
# Use this command to generate a key: openssl rand -hex 32
# SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
# ALGORITHM = "HS256"
# ACCESS_TOKEN_EXPIRE_MINUTES = 30

# =====================================


"""
POST /accounts/login
GET /accounts/me
PUT /accounts/me
DELETE /accounts/me
"""

# =====================================
