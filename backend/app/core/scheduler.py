import asyncio
import logging
import traceback
from datetime import datetime, timezone, timedelta
from typing import Dict, Any
from bson import ObjectId
from app.core.linkedin_service import linkedin_service
from app.config.database import db
import time

logger = logging.getLogger(__name__)

class PostScheduler:
    def __init__(self):
        self.running = False
        self.check_interval = 60  # Check every minute
    
    async def start_scheduler(self):
        """
        Start the post scheduler
        """
        self.running = True
        logger.info("Post scheduler started")
        
        while self.running:
            try:
                logger.debug("Scheduler loop iteration")
                await self.check_and_publish_posts()
                logger.debug(f"Sleeping for {self.check_interval} seconds")
                await asyncio.sleep(self.check_interval)
            except Exception as e:
                logger.error(f"Error in scheduler: {str(e)}")
                logger.error(f"Full traceback: {traceback.format_exc()}")
                await asyncio.sleep(self.check_interval)
    
    async def stop_scheduler(self):
        """
        Stop the post scheduler
        """
        self.running = False
        logger.info("Post scheduler stopped")
    
    async def check_and_publish_posts(self):
        """
        Check for posts that need to be published and publish them
        """
        try:
            # Get the scheduled posts collection
            scheduled_posts_collection = db.get_collection("scheduled_posts")
            
            # Find posts that are pending and scheduled for now or in the past
            # All scheduled times are stored in UTC, so compare with current UTC time
            current_time = datetime.now(timezone.utc)
            
            logger.debug(f"Checking for scheduled posts at {current_time}")
            
            # Find pending posts with scheduled_datetime <= current_time (both in UTC)
            pending_posts = await scheduled_posts_collection.find({
                "status": "pending",
                "scheduled_datetime": {"$lte": current_time}
            }).to_list(length=None)
            
            logger.debug(f"Found {len(pending_posts)} pending posts to publish")
            
            # Log details of pending posts for debugging
            for post in pending_posts:
                logger.debug(f"Pending post {post.get('_id')}: scheduled_datetime={post.get('scheduled_datetime')}, current_time={current_time}")
            
            # Publish each pending post
            for post in pending_posts:
                logger.debug(f"Publishing post {post.get('_id')} with scheduled time {post.get('scheduled_datetime')}")
                await self.publish_post(post)
                
        except Exception as e:
            logger.error(f"Error checking scheduled posts: {str(e)}")
            # Log the full traceback for debugging
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
    
    async def publish_post(self, post: Dict[str, Any]):
        """
        Publish a scheduled post to LinkedIn
        """
        try:
            logger.debug(f"Starting to publish post {post.get('_id')}")
                
            # Get the users collection to get user's LinkedIn token
            users_collection = db.get_collection("users")
            # Convert user_id from string to ObjectId for proper lookup
            user = await users_collection.find_one({"_id": ObjectId(post["user_id"])})
                
            logger.debug(f"User lookup result: {user is not None}")
                
            if not user:
                logger.error(f"User {post['user_id']} not found")
                # Update post status to failed
                scheduled_posts_collection = db.get_collection("scheduled_posts")
                await scheduled_posts_collection.update_one(
                    {"_id": post["_id"]},
                    {"$set": {
                        "status": "failed", 
                        "updated_at": datetime.now(timezone.utc),
                        "error_message": "User not found"
                    }}
                )
                return
                
            # Check if we have a LinkedIn token
            if not user.get("linkedin_token"):
                logger.error(f"User {post['user_id']} has no LinkedIn token")
                # Update post status to failed
                scheduled_posts_collection = db.get_collection("scheduled_posts")
                await scheduled_posts_collection.update_one(
                    {"_id": post["_id"]},
                    {"$set": {
                        "status": "failed", 
                        "updated_at": datetime.now(timezone.utc),
                        "error_message": "User has no LinkedIn token"
                    }}
                )
                return
                
            logger.debug(f"User has LinkedIn token, proceeding to publish")
                
            # Check if we need to refresh the token
            access_token = user["linkedin_token"]
            refresh_token = user.get("linkedin_refresh_token")
            token_expiry = user.get("linkedin_token_expiry")
                
            # If we have an expiry time and it's close to expiring (within 1 day), try to refresh
            if token_expiry and isinstance(token_expiry, datetime):
                # Ensure both datetimes are timezone-aware
                if token_expiry.tzinfo is None:
                    token_expiry = token_expiry.replace(tzinfo=timezone.utc)
                current_time = datetime.now(timezone.utc)
                time_to_expiry = token_expiry - current_time
                if time_to_expiry.total_seconds() < 86400:  # Less than 1 day
                    logger.info(f"Token for user {post['user_id']} is expiring soon, attempting to refresh")
                    if refresh_token:
                        try:
                            refresh_result = linkedin_service.refresh_access_token(refresh_token)
                            if "access_token" in refresh_result:
                                # Update the user with the new token
                                access_token = refresh_result["access_token"]
                                new_expiry = datetime.now(timezone.utc) + timedelta(seconds=refresh_result.get("expires_in", 5184000))  # Default 60 days
                                    
                                await users_collection.update_one(
                                    {"_id": user["_id"]},
                                    {"$set": {
                                        "linkedin_token": access_token,
                                        "linkedin_token_expiry": new_expiry,
                                        "updated_at": datetime.now(timezone.utc)
                                    }}
                                )
                                    
                                logger.info(f"Successfully refreshed token for user {post['user_id']}")
                            else:
                                logger.error(f"Failed to refresh token for user {post['user_id']}: {refresh_result}")
                        except Exception as refresh_error:
                            logger.error(f"Error refreshing token for user {post['user_id']}: {str(refresh_error)}")
                    else:
                        logger.warning(f"Token for user {post['user_id']} is expiring but no refresh token available")
                
            # Publish to LinkedIn (await the async method)
            result = await linkedin_service.post_content(
                access_token,
                user.get("linkedin_member_urn", "urn:li:person:unknown"),
                post["content"]
            )
                
            logger.debug(f"LinkedIn API result: {result}")
                
            # Update post status based on result
            scheduled_posts_collection = db.get_collection("scheduled_posts")
            if not result.get("success", False):
                await scheduled_posts_collection.update_one(
                    {"_id": post["_id"]},
                    {"$set": {
                        "status": "failed", 
                        "updated_at": datetime.now(timezone.utc),
                        "error_message": result.get("message", "Unknown error")
                    }}
                )
                logger.error(f"Failed to publish post {post['_id']}: {result.get('message', 'Unknown error')}")
            else:
                # Extract the post URN from the response (using the correct field name)
                post_urn = result.get("linkedin_post_id", "")
                await scheduled_posts_collection.update_one(
                    {"_id": post["_id"]},
                    {"$set": {
                        "status": "published", 
                        "linkedin_post_id": post_urn,
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )
                logger.info(f"Successfully published post {post['_id']}")
                    
        except Exception as e:
            logger.error(f"Error publishing post {post.get('_id', 'unknown')}: {str(e)}")
            # Log the full traceback for debugging
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Update post status to failed
            scheduled_posts_collection = db.get_collection("scheduled_posts")
            await scheduled_posts_collection.update_one(
                {"_id": post["_id"]},
                {"$set": {
                    "status": "failed", 
                    "updated_at": datetime.now(timezone.utc),
                    "error_message": str(e)
                }}
            )

# Global instance
scheduler = PostScheduler()