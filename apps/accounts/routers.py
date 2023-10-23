from fastapi import APIRouter, status, Depends
from fastapi.security import OAuth2PasswordRequestForm

from apps.accounts import schemas
from apps.accounts.services.authenticate import AccountService, JWT
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


# ------------------------
# --- Password Routers ---
# ------------------------


@router.post(
    '/reset-password',
    status_code=status.HTTP_200_OK,
    response_model=schemas.PasswordResetOut,
    summary='Reset password',
    description="Initiate a password reset request by sending a verification email to the user's "
                "registered email address.",
    tags=['Authentication'])
async def reset_password(payload: schemas.PasswordResetIn):
    return AccountService.reset_password(**payload.model_dump())


@router.post(
    '/reset-password/verify',
    status_code=status.HTTP_200_OK,
    response_model=schemas.PasswordResetVerifyOut,
    summary='Verify reset password',
    description="Verify the password reset request by confirming the provided OTP sent to the user's "
                "registered email address. If the change is successful, the user will need to login again.",
    tags=['Authentication'])
async def verify_reset_password(payload: schemas.PasswordResetVerifyIn):
    return AccountService.verify_reset_password(**payload.model_dump())


# ---------------------
# --- Users Routers ---
# ---------------------

@router.get(
    '/me',
    status_code=status.HTTP_200_OK,
    response_model=schemas.CurrentUserOut,
    summary='Retrieve current user',
    description='Retrieve current user if user is active.',
    tags=['Users'])
async def retrieve_me(current_user: User = Depends(JWT.fetch_user)):
    return {'user': UserManager.to_dict(current_user)}


@router.put(
    '/me',
    status_code=status.HTTP_200_OK,
    response_model=schemas.CurrentUserOut,
    summary='Update current user',
    description='Update current user.',
    tags=['Users'])
async def update_me(payload: schemas.UpdateUserSchema, current_user: User = Depends(JWT.fetch_user)):
    user = UserManager.update_user(current_user.id, **payload.model_dump())
    return {'user': UserManager.to_dict(user)}


@router.post(
    '/me/change-password',
    status_code=status.HTTP_200_OK,
    response_model=schemas.PasswordChangeOut,
    summary='Change current user password',
    description='Change the password for the current user. If the change is successful, the user will '
                'need to login again.',
    tags=['Users'])
async def change_password(payload: schemas.PasswordChangeIn, current_user: User = Depends(JWT.fetch_user)):
    return AccountService.change_password(current_user, **payload.model_dump())


@router.post(
    '/me/change-email',
    status_code=status.HTTP_200_OK,
    response_model=schemas.EmailChangeOut,
    summary='Change current user email',
    description='Change the email address for the current user.',
    tags=['Users'])
async def change_email(email: schemas.EmailChangeIn, current_user: User = Depends(JWT.fetch_user)):
    return AccountService.change_email(current_user, **email.model_dump())


@router.get(
    '/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=schemas.CurrentUserOut,
    summary='Retrieve a single user',
    description='Retrieve a single user by ID. Only admins can read the users data.',
    tags=['Users'],
    dependencies=[Depends(Permission.is_admin)]
)
async def retrieve_user(user_id: int):
    return {'user': UserManager.to_dict(UserManager.get_user(user_id))}

# TODO change email address
# TODO resend otp code
# TODO logout (expire token)
# TODO DELETE /accounts/me
