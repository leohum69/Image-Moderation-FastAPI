# app/database/mongodb.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db = Database()

async def get_database():
    """Create database connection"""
    if db.client is None:
        db.client = AsyncIOMotorClient(
            os.getenv("MONGODB_URI", "mongodb://localhost:27018") # os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        )
        db.database = db.client[os.getenv("DATABASE_NAME", "image_moderation")]
    
    return db.database

async def close_database_connection():
    """Close database connection"""
    if db.client is not None:
        db.client.close()
        db.client = None
        db.database = None

async def get_tokens_collection():
    """Get tokens collection"""
    database = await get_database()
    return database.tokens

async def get_usages_collection():
    """Get usages collection"""
    database = await get_database()
    return database.usages