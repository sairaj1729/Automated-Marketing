import aiohttp
import asyncio
import requests
from app.config.settings import settings
from typing import Dict, Any, Optional
import urllib.parse
import os

class LinkedInService:
    def __init__(self):
        self.client_id = settings.LINKEDIN_CLIENT_ID
        self.client_secret = settings.LINKEDIN_CLIENT_SECRET
        self.redirect_uri = settings.LINKEDIN_REDIRECT_URI or os.getenv("LINKEDIN_REDIRECT_URI", f"{settings.FRONTEND_URL}/callback")
        self.base_url = "https://api.linkedin.com/v2"
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token
        """
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": redirect_uri,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(url, data=data)
        response_data = response.json()
        return response_data
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token using a refresh token
        """
        url = "https://www.linkedin.com/oauth/v2/accessToken"
        data = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        
        response = requests.post(url, data=data)
        response_data = response.json()
        return response_data
    
    def get_user_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Get user profile information using the new OpenID Connect endpoint
        """
        url = f"{self.base_url}/userinfo"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        
        response = requests.get(url, headers=headers)
        response_data = response.json()
        return response_data
    
    def get_detailed_profile(self, access_token: str) -> Dict[str, Any]:
        """
        Get detailed user profile information using the LinkedIn API
        """
        try:
            # First try to get basic profile info
            basic_profile = self.get_user_profile(access_token)
            
            # Try to get additional profile information
            url = f"{self.base_url}/me"
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                detailed_data = response.json()
                # Merge the data
                basic_profile.update(detailed_data)
            
            return basic_profile
        except Exception as e:
            # Return basic profile if detailed fetch fails
            return self.get_user_profile(access_token)
    
    async def post_content(self, access_token: str, member_urn: str, content: str, image_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Post content to LinkedIn
        
        Args:
            access_token: LinkedIn OAuth access token
            member_urn: LinkedIn member URN (e.g., urn:li:person:ABC123)
            content: Content to post
            image_url: Optional image URL to include
            
        Returns:
            Dictionary with success status and LinkedIn post ID
        """
        try:
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"Posting to LinkedIn with access_token: {access_token[:10]}..., member_urn: {member_urn}, content_length: {len(content)}")
            
            # Prepare the post payload
            payload = {
                "author": member_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": content},
                        "shareMediaCategory": "IMAGE" if image_url else "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            logger.debug(f"Payload: {payload}")
            
            # Add image if provided
            if image_url:
                payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "description": {"text": "Image for post"},
                        "media": image_url,
                        "title": {"text": "Image"}
                    }
                ]
            
            # Make the API request
            url = f"{self.base_url}/ugcPosts"
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Making request to {url} with headers: {headers}")
            
            # Use aiohttp for async requests
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    logger.debug(f"Response status: {response.status}")
                    # Check if the request was successful
                    if response.status in (200, 201):
                        response_data = await response.json()
                        logger.debug(f"Success response: {response_data}")
                        linkedin_post_id = response_data.get("id", "")
                        
                        return {
                            "success": True,
                            "linkedin_post_id": linkedin_post_id,
                            "message": "Post published to LinkedIn successfully"
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed response: {error_text}")
                        return {
                            "success": False,
                            "message": f"Failed to post to LinkedIn. Status: {response.status} - {error_text}"
                        }
                    
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Exception in post_content: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return {
                "success": False,
                "message": f"Error posting to LinkedIn: {str(e)}"
            }
    
    async def get_post_engagement(self, access_token: str, post_urn: str) -> Dict[str, Any]:
        """
        Get engagement metrics for a LinkedIn post
        
        Args:
            access_token: LinkedIn OAuth access token
            post_urn: LinkedIn post URN (e.g., urn:li:share:123456789 or just the ID part)
            
        Returns:
            Dictionary with engagement metrics
        """
        try:
            # Ensure we have a proper URN format
            if not post_urn.startswith("urn:li:share:"):
                post_urn = f"urn:li:share:{post_urn}"
            
            # Extract just the ID part for the API call
            if post_urn.startswith("urn:li:share:"):
                post_id = post_urn.replace("urn:li:share:", "")
            else:
                post_id = post_urn
            
            # URL encode the post ID to handle special characters
            encoded_post_id = urllib.parse.quote(post_id, safe='')
            
            # Use the correct endpoint for social actions
            url = f"{self.base_url}/socialActions/{encoded_post_id}"
            
            # Use aiohttp for async requests
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers={
                    "Authorization": f"Bearer {access_token}",
                    "X-Restli-Protocol-Version": "2.0.0"
                }) as response:
                    # Check if the request was successful
                    if response.status == 200:
                        response_data = await response.json()
                        
                        # Parse engagement metrics from response
                        metrics = {
                            "views": 0,
                            "likes": 0,
                            "comments": 0,
                            "shares": 0,
                            "impressions": 0,
                            "engagement_rate": 0.0
                        }
                        
                        # Extract likes count if available
                        if "likesSummary" in response_data:
                            metrics["likes"] = response_data["likesSummary"].get("aggregatedTotalLikes", 0)
                        
                        # Extract comments count if available
                        if "commentsSummary" in response_data:
                            metrics["comments"] = response_data["commentsSummary"].get("aggregatedTotalComments", 0)
                        
                        return {
                            "success": True,
                            "metrics": metrics
                        }
                    elif response.status == 404:
                        # Post not found, return zeros
                        return {
                            "success": True,
                            "metrics": {
                                "views": 0,
                                "likes": 0,
                                "comments": 0,
                                "shares": 0,
                                "impressions": 0,
                                "engagement_rate": 0.0
                            }
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "message": f"Failed to fetch engagement metrics. Status: {response.status} - {error_text}",
                            "metrics": {
                                "views": 0,
                                "likes": 0,
                                "comments": 0,
                                "shares": 0,
                                "impressions": 0,
                                "engagement_rate": 0.0
                            }
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error fetching engagement metrics: {str(e)}",
                "metrics": {
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "impressions": 0,
                    "engagement_rate": 0.0
                }
            }

# Global instance
linkedin_service = LinkedInService()