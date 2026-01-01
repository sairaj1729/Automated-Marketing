from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import os
import pytz
from app.models.user import User
from app.schemas.post import PostGenerateRequest, PostGenerateResponse, ScheduledPostCreate, ScheduledPostUpdate, ScheduledPostResponse, LinkedInPostRequest
from app.api.v1.deps import get_current_active_user
from app.core.ai_service import ai_service
from app.core.linkedin_service import linkedin_service
from app.config.database import db
from app.utils.helpers import is_valid_object_id
from datetime import datetime, timezone, timedelta
from bson import ObjectId

router = APIRouter(prefix="/posts", tags=["Posts"])

@router.post("/generate", response_model=PostGenerateResponse)
async def generate_post(request: PostGenerateRequest, current_user: User = Depends(get_current_active_user)):
    """
    Generate a LinkedIn post using AI
    """
    try:
        # Generate post content using AI service
        generated_content = await ai_service.generate_linkedin_post(
            topic=request.topic,
            tone=request.tone,
            audience=request.audience,
            reference_url=request.url
        )
        
        # Store generated post in database
        generated_posts_collection = db.get_collection("generated_posts")
        post_doc = {
            "user_id": str(current_user.id),
            "topic": request.topic,
            "tone": request.tone,
            "audience": request.audience,
            "url": request.url,
            "generated_content": generated_content,
            "created_at": datetime.utcnow()
        }
        
        await generated_posts_collection.insert_one(post_doc)
        
        return PostGenerateResponse(post=generated_content)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate post: {str(e)}"
        )

@router.post("/generate-public", response_model=PostGenerateResponse)
async def generate_post_public(request: PostGenerateRequest):
    """
    Generate a LinkedIn post using AI (public endpoint for testing)
    """
    try:
        # Generate post content using AI service
        generated_content = await ai_service.generate_linkedin_post(
            topic=request.topic,
            tone=request.tone,
            audience=request.audience,
            reference_url=request.url
        )
        
        return PostGenerateResponse(post=generated_content)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate post: {str(e)}"
        )

@router.post("/scheduled", response_model=ScheduledPostResponse)
async def create_scheduled_post(request: ScheduledPostCreate, timezone_param: str = Query(default=None), current_user: User = Depends(get_current_active_user)):    
    # Use timezone from request body if available, otherwise use query parameter, fallback to default
    effective_timezone = request.timezone or timezone_param or "Asia/Kolkata"
    """
    Schedule a post for later publishing
    """
    # Convert scheduled_datetime from ISO format string to datetime object in UTC
    # The frontend sends time in ISO format with timezone info
    if isinstance(request.scheduled_datetime, str):
        # Handle the case where the frontend sends YYYY-MM-DDTHH:MM format
        if len(request.scheduled_datetime) == 16 and request.scheduled_datetime[10] == 'T':
            # Add seconds to make it a valid ISO format
            scheduled_datetime_str = request.scheduled_datetime + ":00"
        else:
            scheduled_datetime_str = request.scheduled_datetime
            
        try:
            scheduled_dt = datetime.fromisoformat(scheduled_datetime_str)
        except ValueError:
            # If fromisoformat fails, try parsing manually
            try:
                # Split date and time parts
                date_part, time_part = scheduled_datetime_str.split('T')
                year, month, day = map(int, date_part.split('-'))
                hour, minute, second = map(int, time_part.split(':'))
                scheduled_dt = datetime(year, month, day, hour, minute, second)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid datetime format. Expected YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM"
                )
    else:
        scheduled_dt = request.scheduled_datetime
        
    # Handle timezone conversion using pytz for proper timezone handling
    if scheduled_dt.tzinfo is None:
        # If no timezone info, use the effective timezone
        try:
            tz = pytz.timezone(effective_timezone)
            # Localize the datetime to the specified timezone
            scheduled_dt = tz.localize(scheduled_dt)
        except pytz.exceptions.UnknownTimeZoneError:
            # If timezone is unknown, default to Asia/Kolkata (IST)
            tz = pytz.timezone('Asia/Kolkata')
            scheduled_dt = tz.localize(scheduled_dt)
    
    # Convert to UTC for storage
    scheduled_dt_utc = scheduled_dt.astimezone(pytz.UTC)
    
    # Create scheduled post document
    scheduled_post_doc = {
        "user_id": str(current_user.id),
        "content": request.content,
        "scheduled_datetime": scheduled_dt_utc,
        "timezone": effective_timezone,
        "status": "pending",  # pending, published, failed
        "created_at": datetime.now(pytz.UTC),
        "updated_at": datetime.now(pytz.UTC)
    }
    
    # Log the document for debugging
    import logging
    logger = logging.getLogger(__name__)
    logger.debug(f"Creating scheduled post: {scheduled_post_doc}")
    
    # Insert into database
    scheduled_posts_collection = db.get_collection("scheduled_posts")
    result = await scheduled_posts_collection.insert_one(scheduled_post_doc)
    
    # Return response
    scheduled_post_doc["id"] = str(result.inserted_id)
    return ScheduledPostResponse(**scheduled_post_doc)

@router.get("/scheduled", response_model=List[ScheduledPostResponse])
async def get_scheduled_posts(current_user: User = Depends(get_current_active_user)):
    """
    Get all scheduled posts for the current user
    """
    scheduled_posts_collection = db.get_collection("scheduled_posts")
    posts_cursor = scheduled_posts_collection.find({"user_id": str(current_user.id)}).sort("scheduled_datetime", 1)
    posts = await posts_cursor.to_list(length=None)
    
    # Convert to response models
    response_posts = []
    for post in posts:
        post["id"] = str(post["_id"])
        del post["_id"]
        response_posts.append(ScheduledPostResponse(**post))
    
    return response_posts

@router.get("/scheduled/{post_id}", response_model=ScheduledPostResponse)
async def get_scheduled_post(post_id: str, current_user: User = Depends(get_current_active_user)):
    """
    Get a specific scheduled post
    """
    # Validate post ID
    if not is_valid_object_id(post_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid post ID"
        )
    
    # Find post
    scheduled_posts_collection = db.get_collection("scheduled_posts")
    post = await scheduled_posts_collection.find_one({
        "_id": ObjectId(post_id),
        "user_id": str(current_user.id)
    })
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    # Convert to response model
    post["id"] = str(post["_id"])
    del post["_id"]
    return ScheduledPostResponse(**post)

@router.put("/scheduled/{post_id}", response_model=ScheduledPostResponse)
async def update_scheduled_post(
    post_id: str, 
    request: ScheduledPostUpdate, 
    timezone_param: str = Query(default=None),
    current_user: User = Depends(get_current_active_user)
):    
    # Use timezone from request body if available, otherwise use query parameter, fallback to default
    effective_timezone = request.timezone or timezone_param or "Asia/Kolkata"
    """
    Update a scheduled post
    """
    # Validate post ID
    if not is_valid_object_id(post_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid post ID"
        )
    
    # Find post
    scheduled_posts_collection = db.get_collection("scheduled_posts")
    existing_post = await scheduled_posts_collection.find_one({
        "_id": ObjectId(post_id),
        "user_id": str(current_user.id)
    })
    
    if not existing_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    # Prepare update data
    update_data = {}
    if request.content is not None:
        update_data["content"] = request.content
    if request.scheduled_datetime is not None:
        update_data["scheduled_datetime"] = request.scheduled_datetime
        # If the post was failed and we're updating the scheduled time, reset status to pending
        if existing_post.get("status") == "failed":
            update_data["status"] = "pending"
    if request.status is not None:
        update_data["status"] = request.status
    # Always update the timezone when provided
    update_data["timezone"] = effective_timezone
    
    # Only update if there's data to update
    if update_data:
        update_data["updated_at"] = datetime.now(pytz.UTC)
        # Handle scheduled_datetime conversion if it's being updated
        if "scheduled_datetime" in update_data:
            # Check if it's already a datetime object or a string
            if isinstance(update_data["scheduled_datetime"], str):
                # Handle the case where the frontend sends YYYY-MM-DDTHH:MM format
                if len(update_data["scheduled_datetime"]) == 16 and update_data["scheduled_datetime"][10] == 'T':
                    # Add seconds to make it a valid ISO format
                    scheduled_datetime_str = update_data["scheduled_datetime"] + ":00"
                else:
                    scheduled_datetime_str = update_data["scheduled_datetime"]
                    
                try:
                    scheduled_dt = datetime.fromisoformat(scheduled_datetime_str)
                except ValueError:
                    # If fromisoformat fails, try parsing manually
                    try:
                        # Split date and time parts
                        date_part, time_part = scheduled_datetime_str.split('T')
                        year, month, day = map(int, date_part.split('-'))
                        hour, minute, second = map(int, time_part.split(':'))
                        scheduled_dt = datetime(year, month, day, hour, minute, second)
                    except Exception:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid datetime format. Expected YYYY-MM-DDTHH:MM:SS or YYYY-MM-DDTHH:MM"
                        )
                # Convert to UTC for storage if it's not already
                if scheduled_dt.tzinfo is None:
                    # If no timezone info, use the effective timezone
                    try:
                        tz = pytz.timezone(effective_timezone)
                        # Localize the datetime to the specified timezone
                        scheduled_dt = tz.localize(scheduled_dt)
                    except pytz.exceptions.UnknownTimeZoneError:
                        # If timezone is unknown, default to Asia/Kolkata (IST)
                        tz = pytz.timezone('Asia/Kolkata')
                        scheduled_dt = tz.localize(scheduled_dt)
                
                # Convert to UTC for storage
                update_data["scheduled_datetime"] = scheduled_dt.astimezone(pytz.UTC)
            elif isinstance(update_data["scheduled_datetime"], datetime):
                # If it's already a datetime object, ensure it's in UTC
                scheduled_dt = update_data["scheduled_datetime"]
                if scheduled_dt.tzinfo is None:
                    # If no timezone info, use the provided timezone or default to IST
                    try:
                        tz = pytz.timezone(timezone_param)
                        # Localize the datetime to the specified timezone
                        scheduled_dt = tz.localize(scheduled_dt)
                    except pytz.exceptions.UnknownTimeZoneError:
                        # If timezone is unknown, default to Asia/Kolkata (IST)
                        tz = pytz.timezone('Asia/Kolkata')
                        scheduled_dt = tz.localize(scheduled_dt)
                
                # Convert to UTC for storage
                update_data["scheduled_datetime"] = scheduled_dt.astimezone(pytz.UTC)
            
        await scheduled_posts_collection.update_one(
            {"_id": ObjectId(post_id)},
            {"$set": update_data}
        )
    
    # Get updated post
    updated_post = await scheduled_posts_collection.find_one({"_id": ObjectId(post_id)})
    updated_post["id"] = str(updated_post["_id"])
    del updated_post["_id"]
    
    return ScheduledPostResponse(**updated_post)

@router.delete("/scheduled/{post_id}")
async def delete_scheduled_post(post_id: str, current_user: User = Depends(get_current_active_user)):
    """
    Delete a scheduled post
    """
    # Validate post ID
    if not is_valid_object_id(post_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid post ID"
        )
    
    # Find and delete post
    scheduled_posts_collection = db.get_collection("scheduled_posts")
    result = await scheduled_posts_collection.delete_one({
        "_id": ObjectId(post_id),
        "user_id": str(current_user.id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    return {"message": "Scheduled post deleted successfully"}

@router.post("/linkedin", response_model=dict)
async def post_to_linkedin(
    request: LinkedInPostRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Post content to LinkedIn
    
    Args:
        request: LinkedInPostRequest containing access_token, member_urn, content, and optional image_url
        current_user: Current authenticated user
        
    Returns:
        Dictionary with success status and LinkedIn post ID
    """
    try:
        # Post content to LinkedIn (await the async method)
        result = await linkedin_service.post_content(
            access_token=request.access_token,
            member_urn=request.member_urn,
            content=request.content,
            image_url=request.image_url
        )
        
        if result["success"]:
            # Store the post in our database for tracking
            linkedin_posts_collection = db.get_collection("linkedin_posts")
            post_doc = {
                "user_id": str(current_user.id),
                "linkedin_post_id": result["linkedin_post_id"],
                "content": request.content,
                "image_url": request.image_url,
                "posted_at": datetime.utcnow(),
                "status": "published"
            }
            await linkedin_posts_collection.insert_one(post_doc)
            
            return {
                "success": True,
                "message": "Post published to LinkedIn successfully",
                "linkedin_post_id": result["linkedin_post_id"]
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to post to LinkedIn: {str(e)}"
        )