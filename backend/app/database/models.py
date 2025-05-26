# # app/database/models.py
# from pydantic import BaseModel, Field
# from datetime import datetime
# from typing import Optional, Dict, List
# from bson import ObjectId

# class PyObjectId(ObjectId):
#     @classmethod
#     def __get_validators__(cls):
#         yield cls.validate

#     @classmethod
#     def validate(cls, v):
#         if not ObjectId.is_valid(v):
#             raise ValueError("Invalid objectid")
#         return ObjectId(v)

#     @classmethod
#     def __modify_schema__(cls, field_schema):
#         field_schema.update(type="string")

# class Token(BaseModel):
#     id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
#     token: str
#     is_admin: bool = False
#     created_at: datetime = Field(default_factory=datetime.utcnow)
    
#     class Config:
#         allow_population_by_field_name = True
#         arbitrary_types_allowed = True
#         json_encoders = {ObjectId: str}

# class Usage(BaseModel):
#     id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
#     token: str
#     endpoint: str
#     timestamp: datetime = Field(default_factory=datetime.utcnow)
    
#     class Config:
#         allow_population_by_field_name = True
#         arbitrary_types_allowed = True
#         json_encoders = {ObjectId: str}

# class SafetyCategory(BaseModel):
#     category: str
#     confidence: float
#     severity: str  # "low", "medium", "high"

# class ModerationResult(BaseModel):
#     is_safe: bool
#     overall_confidence: float
#     categories: List[SafetyCategory]
#     analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
#     image_hash: Optional[str] = None

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from bson import ObjectId

# Token document model
class Token(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    token: str
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Usage document model  
class Usage(BaseModel):
    id: Optional[ObjectId] = Field(default=None, alias="_id")
    token: str
    endpoint: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

# Safety category for image moderation result
class SafetyCategory(BaseModel):
    category: str
    confidence: float
    severity: str  # e.g., "low", "medium", "high"

# Moderation result schema
class ModerationResult(BaseModel):
    is_safe: bool
    overall_confidence: float
    categories: List[SafetyCategory]
    analysis_timestamp: datetime = Field(default_factory=datetime.utcnow)
    image_hash: Optional[str] = None