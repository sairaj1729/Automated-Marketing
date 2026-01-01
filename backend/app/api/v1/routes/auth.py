from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordRequestForm
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from bson import ObjectId
from app.config.settings import settings
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import Token, TokenData
from app.utils.helpers import get_user_by_email
from app.models.user import User
from app.config.database import db
from app.core.linkedin_service import linkedin_service
from app.api.v1.deps import oauth2_scheme
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate):
    """
    Register a new user
    """
    logger.info(f"Registering user with email: {user_data.email}")
    
    try:
        # Ensure database is connected
        logger.info("Ensuring database is connected")
        if not hasattr(db, 'database') or db.database is None:
            logger.info("Connecting to database")
            db.connect()
        
        # Check if user already exists
        logger.info("Checking if user already exists")
        existing_user = await get_user_by_email(user_data.email)
        logger.info(f"Existing user check result: {existing_user is not None}")
        
        if existing_user:
            logger.warning(f"User with email {user_data.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        logger.info("User does not exist, proceeding with registration")
        
        # Hash password
        logger.info("Hashing password")
        hashed_password = get_password_hash(user_data.password)
        logger.info("Password hashed successfully")
        
        # Create timestamps
        now = datetime.now()
        
        # Create user document
        user_doc = {
            "email": user_data.email,
            "hashed_password": hashed_password,
            "settings": {
                "notifications": {
                    "postReminders": True,
                    "engagementAlerts": True,
                    "weeklyReports": True
                }
            },
            "created_at": now,
            "updated_at": now
        }
        
        logger.info("Inserting user document into database")
        # Insert user into database
        users_collection = db.get_collection("users")
        result = await users_collection.insert_one(user_doc)
        logger.info(f"User inserted with ID: {result.inserted_id}")
        
        if not result.inserted_id:
            logger.error("Failed to insert user into database")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # Return user response
        user_response = UserResponse(
            id=str(result.inserted_id),
            email=user_data.email,
            settings=user_doc["settings"],
            created_at=now,
            updated_at=now
        )
        
        logger.info(f"User registered successfully: {user_response}")
        return user_response
        
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during registration"
        )

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Authenticate user and return access token
    """
    logger.info(f"Login attempt for user: {form_data.username}")
    
    try:
        # Ensure database is connected
        logger.info("Ensuring database is connected")
        if not hasattr(db, 'database') or db.database is None:
            logger.info("Connecting to database")
            db.connect()
        
        # Get user by email
        logger.info("Getting user by email")
        user = await get_user_by_email(form_data.username)
        logger.info(f"User found: {user is not None}")
        
        if not user:
            logger.warning("User not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify password
        logger.info("Verifying password")
        if not verify_password(form_data.password, user.hashed_password):
            logger.warning("Password verification failed")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("Password verified successfully")
        
        # Create access token
        logger.info("Creating access token")
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        logger.info("Login successful")
        return Token(access_token=access_token, token_type="bearer")
        
    except Exception as e:
        logger.error(f"Error during login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during login"
        )


