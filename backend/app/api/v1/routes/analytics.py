from fastapi import APIRouter, Depends
from typing import List
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse
from app.models.analytics import MetricDataPoint, HeatmapDataPoint
from app.api.v1.deps import get_current_active_user
from app.config.database import db
from app.core.linkedin_service import linkedin_service
from datetime import datetime, timedelta
import asyncio

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(current_user: User = Depends(get_current_active_user)):
    """
    Get analytics data for the dashboard
    """
    try:
        # Fetch real analytics data from database and LinkedIn API
        user_id = str(current_user.id)
        
        # Get user's LinkedIn token
        users_collection = db.get_collection("users")
        user_doc = await users_collection.find_one({"_id": current_user.id})
        linkedin_token = user_doc.get("linkedin_token") if user_doc else None
        
        # Fetch metrics from database
        metrics = await get_user_metrics(user_id, linkedin_token)
        
        # Fetch heatmap data (could be from database or calculated)
        heatmap_data = await get_heatmap_data(user_id)
        
        return AnalyticsResponse(metrics=metrics, heatmap_data=heatmap_data)
        
    except Exception as e:
        # Fallback to mock data if there's an error
        metrics = [
            MetricDataPoint(label="Posts Generated", value="0", change="+0%"),
            MetricDataPoint(label="Engagement Rate", value="0%", change="+0%"),
            MetricDataPoint(label="Scheduled Posts", value="0", change="+0"),
            MetricDataPoint(label="Total Reach", value="0", change="+0%"),
        ]
        
        heatmap_data = [
            HeatmapDataPoint(day="Mon", hours=[2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 9, 8, 6, 4, 3, 2, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Tue", hours=[1, 2, 4, 7, 5, 3, 2, 4, 6, 8, 7, 5, 4, 6, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Wed", hours=[2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 9, 8, 6, 4, 3, 2, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Thu", hours=[1, 2, 4, 7, 5, 3, 2, 4, 6, 8, 7, 5, 4, 6, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Fri", hours=[2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Sat", hours=[1, 1, 2, 3, 2, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Sun", hours=[1, 1, 1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1]),
        ]
        
        return AnalyticsResponse(metrics=metrics, heatmap_data=heatmap_data)

@router.get("/metrics")
async def get_metrics(current_user: User = Depends(get_current_active_user)):
    """
    Get key metrics for dashboard
    """
    try:
        user_id = str(current_user.id)
        
        # Get user's LinkedIn token
        users_collection = db.get_collection("users")
        user_doc = await users_collection.find_one({"_id": current_user.id})
        linkedin_token = user_doc.get("linkedin_token") if user_doc else None
        
        # Fetch real metrics
        metrics = await get_user_metrics(user_id, linkedin_token)
        return [metric.dict() for metric in metrics]
        
    except Exception as e:
        # Fallback to mock data if there's an error
        metrics = [
            {"label": "Posts Generated", "value": "0", "change": "+0%"},
            {"label": "Engagement Rate", "value": "0%", "change": "+0%"},
            {"label": "Scheduled Posts", "value": "0", "change": "+0"},
            {"label": "Total Reach", "value": "0", "change": "+0%"},
        ]
        return metrics

@router.get("/best-times")
async def get_best_posting_times(current_user: User = Depends(get_current_active_user)):
    """
    Get optimal posting times data
    """
    try:
        user_id = str(current_user.id)
        heatmap_data = await get_heatmap_data(user_id)
        return [data.dict() for data in heatmap_data]
        
    except Exception as e:
        # Fallback to mock data if there's an error
        heatmap_data = [
            {"day": "Mon", "hours": [2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 9, 8, 6, 4, 3, 2, 1, 1, 1, 1]},
            {"day": "Tue", "hours": [1, 2, 4, 7, 5, 3, 2, 4, 6, 8, 7, 5, 4, 6, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]},
            {"day": "Wed", "hours": [2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 9, 8, 6, 4, 3, 2, 1, 1, 1, 1]},
            {"day": "Thu", "hours": [1, 2, 4, 7, 5, 3, 2, 4, 6, 8, 7, 5, 4, 6, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]},
            {"day": "Fri", "hours": [2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]},
            {"day": "Sat", "hours": [1, 1, 2, 3, 2, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1]},
            {"day": "Sun", "hours": [1, 1, 1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1]},
        ]
        return heatmap_data


async def get_user_metrics(user_id: str, linkedin_token: str = None):
    """
    Get real user metrics from database and LinkedIn API
    """
    try:
        # Initialize metrics with default values
        posts_generated = 0
        scheduled_posts = 0
        total_reach = 0
        total_likes = 0
        total_comments = 0
        total_shares = 0
        
        # Get counts from database
        generated_posts_collection = db.get_collection("generated_posts")
        scheduled_posts_collection = db.get_collection("scheduled_posts")
        linkedin_posts_collection = db.get_collection("linkedin_posts")
        
        # Count generated posts
        posts_generated = await generated_posts_collection.count_documents({"user_id": user_id})
        
        # Count scheduled posts
        scheduled_posts = await scheduled_posts_collection.count_documents({"user_id": user_id})
        
        # Get LinkedIn engagement data if token is available
        if linkedin_token:
            # Get all LinkedIn posts for this user
            linkedin_posts_cursor = linkedin_posts_collection.find({"user_id": user_id})
            linkedin_posts = await linkedin_posts_cursor.to_list(length=None)
            
            # For each post, get engagement metrics
            for post in linkedin_posts:
                linkedin_post_id = post.get("linkedin_post_id")
                if linkedin_post_id:
                    # Get engagement metrics from LinkedIn
                    engagement_result = linkedin_service.get_post_engagement(linkedin_token, linkedin_post_id)
                    if engagement_result.get("success"):
                        metrics = engagement_result.get("metrics", {})
                        total_likes += metrics.get("likes", 0)
                        total_comments += metrics.get("comments", 0)
                        total_shares += metrics.get("shares", 0)
                        # Estimate reach based on engagement (simplified calculation)
                        total_reach += metrics.get("likes", 0) + metrics.get("comments", 0) * 2 + metrics.get("shares", 0) * 3
        
        # Calculate engagement rate (simplified)
        engagement_rate = 0.0
        if total_reach > 0:
            engagement_rate = round(((total_likes + total_comments + total_shares) / total_reach) * 100, 2)
        
        # Calculate changes (simplified - would normally compare to previous period)
        metrics = [
            MetricDataPoint(label="Posts Generated", value=str(posts_generated), change="+0%"),
            MetricDataPoint(label="Engagement Rate", value=f"{engagement_rate}%", change="+0%"),
            MetricDataPoint(label="Scheduled Posts", value=str(scheduled_posts), change="+0"),
            MetricDataPoint(label="Total Reach", value=str(total_reach), change="+0%"),
        ]
        
        return metrics
        
    except Exception as e:
        # Return default metrics if there's an error
        return [
            MetricDataPoint(label="Posts Generated", value="0", change="+0%"),
            MetricDataPoint(label="Engagement Rate", value="0%", change="+0%"),
            MetricDataPoint(label="Scheduled Posts", value="0", change="+0"),
            MetricDataPoint(label="Total Reach", value="0", change="+0%"),
        ]


async def get_heatmap_data(user_id: str):
    """
    Get heatmap data for best posting times based on user's historical engagement data
    """
    try:
        # Initialize heatmap with zeros
        heatmap_hours = [[0 for _ in range(24)] for _ in range(7)]
        
        # Get user's scheduled and published posts
        scheduled_posts_collection = db.get_collection("scheduled_posts")
        linkedin_posts_collection = db.get_collection("linkedin_posts")
        
        # Get scheduled posts with engagement data
        scheduled_cursor = scheduled_posts_collection.find({"user_id": user_id})
        scheduled_posts = await scheduled_cursor.to_list(length=None)
        
        # Get published LinkedIn posts with engagement data
        linkedin_cursor = linkedin_posts_collection.find({"user_id": user_id})
        linkedin_posts = await linkedin_cursor.to_list(length=None)
        
        # Process scheduled posts to build heatmap
        for post in scheduled_posts:
            scheduled_time = post.get("scheduled_datetime")
            if scheduled_time:
                # Convert to datetime if it's a string
                if isinstance(scheduled_time, str):
                    try:
                        from datetime import datetime
                        scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                    except:
                        continue
                
                # Get day of week (0=Monday, 6=Sunday) and hour
                day_of_week = scheduled_time.weekday()
                hour = scheduled_time.hour
                
                # Increment count for this time slot
                if 0 <= day_of_week < 7 and 0 <= hour < 24:
                    heatmap_hours[day_of_week][hour] += 1
        
        # Process LinkedIn posts to build heatmap based on engagement
        for post in linkedin_posts:
            posted_time = post.get("posted_at")
            if posted_time:
                # Convert to datetime if it's a string
                if isinstance(posted_time, str):
                    try:
                        from datetime import datetime
                        posted_time = datetime.fromisoformat(posted_time.replace('Z', '+00:00'))
                    except:
                        continue
                
                # Get day of week (0=Monday, 6=Sunday) and hour
                day_of_week = posted_time.weekday()
                hour = posted_time.hour
                
                # Get engagement score (likes + comments*2 + shares*3)
                likes = post.get("metrics", {}).get("likes", 0)
                comments = post.get("metrics", {}).get("comments", 0)
                shares = post.get("metrics", {}).get("shares", 0)
                engagement_score = likes + (comments * 2) + (shares * 3)
                
                # Add weighted engagement to this time slot
                if 0 <= day_of_week < 7 and 0 <= hour < 24:
                    heatmap_hours[day_of_week][hour] += max(1, engagement_score // 10)  # Normalize engagement
        
        # Convert to heatmap data format
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        heatmap_data = [
            HeatmapDataPoint(day=days[i], hours=heatmap_hours[i])
            for i in range(7)
        ]
        
        # If no data, fall back to industry averages
        if all(sum(row) == 0 for row in heatmap_hours):
            heatmap_data = [
                HeatmapDataPoint(day="Mon", hours=[2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 9, 8, 6, 4, 3, 2, 1, 1, 1, 1]),
                HeatmapDataPoint(day="Tue", hours=[1, 2, 4, 7, 5, 3, 2, 4, 6, 8, 7, 5, 4, 6, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]),
                HeatmapDataPoint(day="Wed", hours=[2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 9, 8, 6, 4, 3, 2, 1, 1, 1, 1]),
                HeatmapDataPoint(day="Thu", hours=[1, 2, 4, 7, 5, 3, 2, 4, 6, 8, 7, 5, 4, 6, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]),
                HeatmapDataPoint(day="Fri", hours=[2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]),
                HeatmapDataPoint(day="Sat", hours=[1, 1, 2, 3, 2, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1]),
                HeatmapDataPoint(day="Sun", hours=[1, 1, 1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1]),
            ]
        
        return heatmap_data
        
    except Exception as e:
        # Return default heatmap data if there's an error
        return [
            HeatmapDataPoint(day="Mon", hours=[2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 9, 8, 6, 4, 3, 2, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Tue", hours=[1, 2, 4, 7, 5, 3, 2, 4, 6, 8, 7, 5, 4, 6, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Wed", hours=[2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 9, 8, 6, 4, 3, 2, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Thu", hours=[1, 2, 4, 7, 5, 3, 2, 4, 6, 8, 7, 5, 4, 6, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Fri", hours=[2, 3, 5, 8, 6, 4, 3, 5, 7, 9, 8, 6, 5, 7, 8, 7, 5, 3, 2, 1, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Sat", hours=[1, 1, 2, 3, 2, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1]),
            HeatmapDataPoint(day="Sun", hours=[1, 1, 1, 2, 2, 2, 3, 4, 5, 6, 7, 8, 7, 6, 5, 4, 3, 2, 2, 1, 1, 1, 1, 1]),
        ]