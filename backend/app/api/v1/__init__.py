from fastapi import APIRouter
from app.api.v1.routes import auth, users, posts, analytics, settings, emails
from app.api.v1.routes import linkedin_auth

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(posts.router)
api_router.include_router(analytics.router)
api_router.include_router(settings.router)
api_router.include_router(emails.router)
api_router.include_router(linkedin_auth.router)