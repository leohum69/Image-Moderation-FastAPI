# app/auth_service.py
import uuid
from datetime import datetime
from typing import Optional, List

from database.models import Token, Usage
from database.mongodb import get_tokens_collection, get_usages_collection

class AuthService:
    
    async def create_token(self, is_admin: bool = False) -> Token:
        """Create a new bearer token"""
        token = Token(
            token=str(uuid.uuid4()),
            is_admin=is_admin,
            created_at=datetime.utcnow()
        )
        
        collection = await get_tokens_collection()
        # Use dict() instead of model_dump for Pydantic v1 compatibility
        result = await collection.insert_one(token.dict(by_alias=True))
        token.id = result.inserted_id
        
        return token
    
    async def validate_token(self, token_str: str) -> Optional[Token]:
        """Validate a bearer token"""
        collection = await get_tokens_collection()
        token_data = await collection.find_one({"token": token_str})
        
        if token_data:
            # Debug prints
            print(f"Raw token_data from MongoDB: {token_data}")
            print(f"Type of _id: {type(token_data.get('_id'))}")
            print(f"Value of _id: {token_data.get('_id')}")
            
            # The key fix: ensure proper handling of MongoDB data
            try:
                token_obj = Token(**token_data)
                print(f"Successfully created Token object: {token_obj}")
                return token_obj
            except Exception as e:
                print(f"Error creating Token object: {e}")
                print(f"Exception type: {type(e)}")
                import traceback
                traceback.print_exc()
                return None
        else:
            print(f"No token found for: {token_str}")
        return None
    
    async def get_all_tokens(self) -> List[Token]:
        """Get all tokens (admin only)"""
        collection = await get_tokens_collection()
        cursor = collection.find({})
        tokens = []
        async for token_data in cursor:
            try:
                tokens.append(Token(**token_data))
            except Exception as e:
                print(f"Error creating Token object: {e}")
                print(f"Token data: {token_data}")
                continue
        return tokens
    
    async def delete_token(self, token_str: str) -> bool:
        """Delete a specific token"""
        collection = await get_tokens_collection()
        result = await collection.delete_one({"token": token_str})
        return result.deleted_count > 0
    
    async def log_usage(self, token_str: str, endpoint: str):
        """Log API usage"""
        usage = Usage(
            token=token_str,
            endpoint=endpoint,
            timestamp=datetime.utcnow()
        )
        
        collection = await get_usages_collection()
        # Use dict() instead of model_dump for Pydantic v1 compatibility
        await collection.insert_one(usage.dict(by_alias=True))