from fastapi import APIRouter, Request, HTTPException, Query, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
import urllib.parse
from app.config.settings import settings
from app.api.v1.deps import oauth2_scheme
from app.core.linkedin_service import linkedin_service
from app.utils.helpers import get_user_by_email
from app.config.database import db
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Optional
import logging
from pydantic import BaseModel
from typing import Optional

class LinkedInCallbackRequest(BaseModel):
    code: str

class LinkedInProfileResponse(BaseModel):
    name: str
    headline: Optional[str] = None
    profile_picture_url: Optional[str] = None

router = APIRouter(prefix="/linkedin", tags=["LinkedIn Auth"])

@router.get("/auth")
async def linkedin_auth(
    redirect_uri: str = Query(..., description="Redirect URI after authentication"),
    scope: str = Query("openid profile email w_member_social", description="LinkedIn API scopes")
):
    """
    Initiate LinkedIn OAuth flow
    """
    # Build the LinkedIn authorization URL
    linkedin_auth_url = (
        f"https://www.linkedin.com/oauth/v2/authorization?"
        f"response_type=code&"
        f"client_id={settings.LINKEDIN_CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}&"
        f"scope={urllib.parse.quote(scope)}"
    )
    
    # Return redirect response to LinkedIn
    return RedirectResponse(url=linkedin_auth_url)


@router.post("/callback")
async def linkedin_callback(request: LinkedInCallbackRequest, token: str = Depends(oauth2_scheme)):
    """
    Handle LinkedIn OAuth callback and exchange code for access token
    """
    logger = logging.getLogger(__name__)
    logger.info("LinkedIn callback endpoint called")
    logger.info(f"Request data: {request}")
    logger.info(f"Token: {token[:20] if token else 'None'}...")
    
    try:
        # Decode the user token to identify the authenticated user
        from app.schemas.auth import TokenData
        from app.core.security import decode_access_token
        
        token_data_decoded = decode_access_token(token)
        if not token_data_decoded or not token_data_decoded.email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate user credentials"
            )
        
        # Get the authenticated user
        user = await get_user_by_email(token_data_decoded.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Authenticated user not found"
            )
        
        # Exchange code for access token
        redirect_uri = settings.LINKEDIN_REDIRECT_URI or f"{settings.FRONTEND_URL}/callback"
        
        logger.info(f"Exchanging code for token with redirect_uri: {redirect_uri}")
        logger.info(f"Authorization code: {request.code[:10] if request.code else 'None'}...")
        
        token_data = linkedin_service.exchange_code_for_token(
            request.code, redirect_uri
        )
        
        logger.info(f"Token exchange response: {token_data}")
        
        if "error" in token_data:
            error_detail = f"LinkedIn authentication failed: {token_data.get('error_description', 'Unknown error')}"
            logger.error(error_detail)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_detail
            )
        
        # Get user profile to retrieve member URN
        logger.info("Fetching user profile from LinkedIn")
        try:
            profile_data = linkedin_service.get_detailed_profile(token_data["access_token"])
            logger.info(f"Profile data: {profile_data}")
        except Exception as profile_error:
            logger.error(f"Error fetching profile: {profile_error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to fetch LinkedIn profile: {str(profile_error)}"
            )
        
        if "sub" in profile_data:
            member_urn = f"urn:li:person:{profile_data['sub']}"
        else:
            member_urn = "urn:li:person:unknown"
        
        # Extract relevant profile information
        profile_info = {
            "name": profile_data.get("name", "LinkedIn User"),
            "headline": profile_data.get("headline", "Professional"),
            "picture": profile_data.get("picture", None)
        }
        
        # Calculate token expiry time (default 60 days for LinkedIn)
        from datetime import timezone
        token_expiry = datetime.now(timezone.utc) + timedelta(seconds=token_data.get("expires_in", 5184000))
        
        # Update user document with LinkedIn token, refresh token, member URN, and profile data
        users_collection = db.get_collection("users")
        update_data = {
            "linkedin_token": token_data["access_token"],
            "linkedin_member_urn": member_urn,
            "linkedin_profile": profile_info,
            "linkedin_token_expiry": token_expiry,
            "updated_at": datetime.now()
        }
        
        # Add refresh token if provided
        if "refresh_token" in token_data:
            update_data["linkedin_refresh_token"] = token_data["refresh_token"]
        
        # Log the user ID for debugging
        logger.info(f"Updating user with ID: {user.id} (type: {type(user.id)})")
        
        # Convert user ID to ObjectId if it's a string
        user_id = ObjectId(user.id) if isinstance(user.id, str) else user.id
        
        await users_collection.update_one(
            {"_id": user_id},  # Update the authenticated user
            {"$set": update_data}
        )
        
        # Verify the update was successful
        updated_user = await users_collection.find_one({"_id": user.id})
        if updated_user and updated_user.get("linkedin_token"):
            logger.info("Successfully updated user with LinkedIn token")
        else:
            logger.error("Failed to update user with LinkedIn token")
        
        return {
            "access_token": token_data["access_token"],
            "token_type": token_data.get("token_type", "Bearer"),
            "expires_in": token_data.get("expires_in", 0),
            "refresh_token": token_data.get("refresh_token", ""),
            "member_urn": member_urn,
            "profile": profile_info
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to authenticate with LinkedIn: {str(e)}"
        )