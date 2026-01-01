from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

    @classmethod
    def connect(cls):
        cls.client = AsyncIOMotorClient(settings.MONGODB_URL)
        cls.database = cls.client[settings.MONGODB_DATABASE]
        print(f"Connected to MongoDB database: {settings.MONGODB_DATABASE}")

    @classmethod
    def close(cls):
        if cls.client:
            cls.client.close()
            print("Closed MongoDB connection")

    @classmethod
    def get_collection(cls, collection_name: str):
        if cls.database is None:
            raise RuntimeError("Database not initialized. Call connect() first.")
        return cls.database[collection_name]

db = Database()