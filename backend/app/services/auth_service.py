from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate, UserResponse
from fastapi import HTTPException, status
from datetime import timedelta


class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> UserResponse:
        """Register a new user with validation"""
        # Check if email already exists
        existing = db.execute(select(User).where(User.email == user_data.email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already registered")

        # Check if username already exists
        existing_username = db.execute(select(User).where(User.username == user_data.username)).first()
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")

        # Create new user with hashed password
        hashed_pwd = hash_password(user_data.password)
        new_user = User(
            email=user_data.email,
            username=user_data.username,
            full_name=user_data.full_name,
            hashed_password=hashed_pwd
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        return UserResponse.model_validate(new_user)

    @staticmethod
    def login_user(db: Session, email: str, password: str) -> tuple[User, str]:
        """Authenticate user and generate JWT token"""
        # Find user by email
        user = db.execute(select(User).where(User.email == email)).scalars().first()
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not user.is_active:
            raise HTTPException(status_code=403, detail="User account is inactive")

        # Generate token with 24-hour expiry
        access_token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(hours=24)
        )

        return user, access_token

    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        """Get user by ID"""
        user = db.execute(select(User).where(User.id == user_id)).scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
