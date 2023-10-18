from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from apps.accounts import schemas
from apps.accounts.services.auth import AccountService, AuthToken
from apps.accounts.services.permissions import Permission
from apps.accounts.services.user import User, UserManager

router = APIRouter(
    prefix='/accounts'
)


# ------------------------
# --- Register Routers ---
# ------------------------

@router.post(
    '/register',
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.RegisterOut,
    summary='Register a new user',
    description='Register a new user by email and password.',
    tags=['Authentication'])
async def register(payload: schemas.RegisterIn):
    return AccountService.register(**payload.model_dump(exclude={"password_confirm"}))


@router.post(
    '/register/verify',
    status_code=status.HTTP_200_OK,
    response_model=schemas.RegisterVerifyOut,
    summary='Verify user registration',
    description='Verify a new user registration by confirming the provided OTP.',
    tags=['Authentication'])
async def verify_registration(payload: schemas.RegisterVerifyIn):
    return AccountService.verify_registration(**payload.model_dump())


# ---------------------
# --- Login Routers ---
# ---------------------

@router.post(
    '/login',
    status_code=status.HTTP_200_OK,
    response_model=schemas.LoginOut,
    summary='Login a user',
    description='Login a user with valid credentials, if user account is active.',
    tags=['Authentication'])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return AccountService.login(form_data.username, form_data.password)


# ---------------------
# --- Users Routers ---
# ---------------------

@router.get(
    '/me/',
    status_code=status.HTTP_200_OK,
    response_model=schemas.CurrentUserOut,
    summary='Retrieve current user',
    description='Retrieve current user if user is active.',
    tags=['Users'])
async def retrieve_me(current_user: User = Depends(AuthToken.fetch_user_by_token)):
    return {'user': UserManager.to_dict(current_user)}


@router.get(
    '/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=schemas.CurrentUserOut,
    summary='Retrieve a single user',
    description='Retrieve a single user by ID.',
    tags=['Users'],
    dependencies=[Depends(Permission.is_admin)]
)
async def retrieve_user(user_id: int):
    """
    Only admins can read the users data.
    """
    return {'user': UserManager.to_dict(UserManager.get_user(user_id))}

# TODO PUT /accounts/me
# TODO DELETE /accounts/me
# TODO Reset Password
# TODO change email address
# TODO resend otp code
# TODO add Permission (admin and user)
