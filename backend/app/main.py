from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.database import db
from app.config.settings import settings
from app.api.v1 import api_router
from app.core.scheduler import scheduler
import asyncio

# Create FastAPI app
app = FastAPI(
    title="LinkedIn AutoMarketer API",
    description="Backend API for LinkedIn marketing automation tool",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL,"https://automated-marketing-flame.vercel.app", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Event handlers
@app.on_event("startup")
async def startup_event():
    """
    Startup event handler
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Connect to database
    db.connect()
    logger.info("Database connected")
    
    # Start the post scheduler
    logger.info("Starting post scheduler")
    asyncio.create_task(scheduler.start_scheduler())
    logger.info("Post scheduler started")

@app.on_event("shutdown")
async def shutdown_event():
    """
    Shutdown event handler
    """
    # Stop the post scheduler
    await scheduler.stop_scheduler()
    
    # Close database connection
    db.close()

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Health check endpoint
@app.get("/")
async def root():
    """
    Root endpoint - health check
    """
    return {"message": "LinkedIn AutoMarketer API is running"}
    
@app.api_route("/health", methods=["GET", "HEAD"], include_in_schema=False)
async def health_check():
    return Response(status_code=200)


# Debug endpoint to check token
@app.get("/debug/token")
async def debug_token(token: str):
    """
    Debug endpoint to check if a token is valid
    """
    from app.core.security import decode_access_token
    from app.utils.helpers import get_user_by_email
    import logging
    
    logger = logging.getLogger(__name__)
    logger.debug(f"Debugging token: {token[:20]}...")
    
    token_data = decode_access_token(token)
    if not token_data or not token_data.email:
        logger.warning("Could not validate credentials - token data invalid")
        return {"valid": False, "error": "Could not validate credentials"}
    
    logger.debug(f"Token data email: {token_data.email}")
    user = await get_user_by_email(token_data.email)
    if not user:
        logger.warning(f"User not found: {token_data.email}")
        return {"valid": False, "error": "User not found"}
    
    logger.debug(f"User found: {user.email}")
    return {"valid": True, "user": user.email}