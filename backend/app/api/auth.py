from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - **email**: User email (must be unique)
    - **username**: Username (must be unique)
    - **password**: User password (will be hashed)
    - **full_name**: Optional full name
    """
    return AuthService.register_user(db, user_data)


@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Login user and get access token.

    - **email**: User email
    - **password**: User password

    Returns JWT access token valid for 24 hours.
    """
    user, token = AuthService.login_user(db, login_data.email, login_data.password)
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information.

    Requires valid JWT token in Authorization header.
    """
    return UserResponse.model_validate(current_user)
