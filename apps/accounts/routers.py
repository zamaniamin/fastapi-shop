from fastapi import APIRouter, status

from apps.products import schemas

router = APIRouter(
    prefix="/accounts",
    tags=["Authentication"]
)

# to get a string like this run:
# Use this command to generate a key: openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.UserSchema,
    summary='Register a new user',
    description='Register a new user by email,for now with email.')
# TODO rename `user_data` to `register`
async def register(user_data: schemas.UserRegisterSchema):
    # TODO create a new class `OAuthService` and move the code block to it.
    # example: registered = OAuthService.register(**register.model_dump())
    user = UserManager.create_user(user_data.model_dump(exclude={"confirm"}))

    # TODO move this code to `OAuthService.register`
    EmailHandler.send_totp_email(totp.generate_totp(user.totp_secret))

    # TODO `return {'register': register}` , or ask from AI
    return schemas.UserSchema.model_validate(user)


"""
POST /accounts/login
POST /accounts/register
GET /accounts/me
PUT /accounts/me
DELETE /accounts/me
"""
