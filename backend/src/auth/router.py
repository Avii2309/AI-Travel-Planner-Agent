"""HTTP endpoints for local JWT authentication."""

from fastapi import APIRouter, HTTPException, status

from src.auth.schemas import AccessTokenResponse, LoginRequest, RegisterRequest, UserResponse
from src.auth.security import CurrentUserDependency, create_access_token
from src.auth.service import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
    authenticate_user,
    register_user,
)
from src.presentation.api.dependencies import DatabaseSessionDependency, SettingsDependency

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
)
async def register(
    request: RegisterRequest,
    session: DatabaseSessionDependency,
) -> UserResponse:
    """Register a user with a unique email and bcrypt-hashed password."""

    try:
        return await register_user(session, request)
    except EmailAlreadyRegisteredError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from error


@router.post(
    "/login",
    response_model=AccessTokenResponse,
    summary="Log in and receive a JWT access token",
)
async def login(
    request: LoginRequest,
    session: DatabaseSessionDependency,
    settings: SettingsDependency,
) -> AccessTokenResponse:
    """Authenticate credentials and issue a short-lived Bearer access token."""

    try:
        user = await authenticate_user(session, str(request.email), request.password)
    except InvalidCredentialsError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from error
    return AccessTokenResponse(access_token=create_access_token(user.id, settings))


@router.get("/me", response_model=UserResponse, summary="Get the current authenticated user")
async def get_me(current_user: CurrentUserDependency) -> UserResponse:
    """Return the user identified by a valid Bearer access token."""

    return current_user
