from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from app.core.security import decode_access_token
from app.utils.helpers import get_user_by_email
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Get the current authenticated user from the token
    """
    logger.debug(f"Validating token: {token[:20]}...")
    token_data = decode_access_token(token)
    if not token_data or not token_data.email:
        logger.warning("Could not validate credentials - token data invalid")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"Token data email: {token_data.email}")
    user = await get_user_by_email(token_data.email)
    if not user:
        logger.warning(f"User not found: {token_data.email}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.debug(f"User found: {user.email}")
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get the current active user
    """
    # In a real application, you might check if the user is active
    # For now, we'll just return the current user
    return current_user