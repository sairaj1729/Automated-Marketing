from typing import Optional
from bson import ObjectId
from app.config.database import db
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

async def get_user_by_email(email: str) -> Optional[User]:
    """
    Get a user by email from the database
    """
    # Ensure database is connected
    if not hasattr(db, 'database') or db.database is None:
        logger.info("Connecting to database in get_user_by_email")
        db.connect()
    
    users_collection = db.get_collection("users")
    user_doc = await users_collection.find_one({"email": email})
    
    if user_doc:
        # Convert _id to id for Pydantic model
        user_doc["id"] = str(user_doc["_id"])
        del user_doc["_id"]
        return User(**user_doc)
    
    return None

async def get_user_by_id(user_id: str) -> Optional[User]:
    """
    Get a user by ID from the database
    """
    # Ensure database is connected
    if not hasattr(db, 'database') or db.database is None:
        logger.info("Connecting to database in get_user_by_id")
        db.connect()
    
    users_collection = db.get_collection("users")
    try:
        user_doc = await users_collection.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None
    
    if user_doc:
        # Convert _id to id for Pydantic model
        user_doc["id"] = str(user_doc["_id"])
        del user_doc["_id"]
        return User(**user_doc)
    
    return None

def is_valid_object_id(oid: str) -> bool:
    """
    Check if a string is a valid MongoDB ObjectId
    """
    try:
        ObjectId(oid)
        return True
    except Exception:
        return False