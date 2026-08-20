"""User-related API routes"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import User, UserPreferences
from schemas import UserCreate, UserResponse, LoginRequest, TokenResponse, PrivacySettings
from auth import AuthService, get_current_user
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    - **username**: Unique username (3-50 chars)
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars)
    - **full_name**: Optional full name
    """
    # Check if user exists
    existing_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    
    # Create new user
    try:
        new_user = User(
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            hashed_password=AuthService.hash_password(user.password)
        )
        db.add(new_user)
        db.flush()  # Get user ID without committing
        
        # Create user preferences
        preferences = UserPreferences(user_id=new_user.id)
        db.add(preferences)
        
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {user.username}")
        return new_user
    
    except Exception as e:
        db.rollback()
        logger.error(f"User registration error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Login user and get access token
    
    Returns JWT token for authentication
    """
    user = db.query(User).filter(User.username == credentials.username).first()
    
    if not user or not AuthService.verify_password(
        credentials.password,
        user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create token
    access_token = AuthService.create_access_token(
        data={"sub": user.id, "username": user.username},
        expires_delta=timedelta(minutes=30)
    )
    
    logger.info(f"User logged in: {user.username}")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 30 * 60
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current user profile
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put("/me/privacy", response_model=dict)
async def update_privacy_settings(
    settings: PrivacySettings,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update user privacy settings
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.data_retention_days = settings.data_retention_days
    user.auto_delete_enabled = settings.auto_delete_enabled
    user.allow_data_export = settings.allow_data_export
    
    db.commit()
    logger.info(f"Privacy settings updated for user: {user.username}")
    
    return {"message": "Privacy settings updated successfully"}


@router.delete("/me")
async def delete_account(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete user account and all associated data
    """
    user = db.query(User).filter(User.id == current_user["user_id"]).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    try:
        db.delete(user)  # Cascade delete will remove sessions, metrics, etc.
        db.commit()
        logger.info(f"User account deleted: {user.username}")
        return {"message": "Account deleted successfully"}
    except Exception as e:
        db.rollback()
        logger.error(f"Account deletion error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
