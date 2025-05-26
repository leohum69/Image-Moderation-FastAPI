# backend/main.py
from fastapi import FastAPI, HTTPException, Depends, status, File, UploadFile
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os
from typing import Optional, List
import uuid
import asyncio
from PIL import Image
import io

from database.mongodb import get_database, close_database_connection
from database.models import Token, Usage, ModerationResult
from auth_service import AuthService
from image_analyzer import ImageAnalyzer

app = FastAPI(
    title="Image Moderation API",
    description="API for moderating images and detecting harmful content",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on your frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Initialize services
auth_service = AuthService()
image_analyzer = ImageAnalyzer()

# Startup and shutdown events
@app.on_event("startup")
async def startup_db_client():
    await get_database()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_database_connection()

# Dependency to get current user token
async def get_current_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Token:
    token = await auth_service.validate_token(credentials.credentials)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Log usage
    await auth_service.log_usage(credentials.credentials, "validate_token")
    return token

# Dependency for admin-only endpoints
async def get_admin_token(token: Token = Depends(get_current_token)) -> Token:
    if not token.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return token

# Auth endpoints (Admin only)
@app.post("/auth/tokens", response_model=dict)
async def create_token(
    is_admin: bool = False,
    admin_token: Token = Depends(get_admin_token)
):
    """Create a new bearer token"""
    token = await auth_service.create_token(is_admin=is_admin)
    await auth_service.log_usage(admin_token.token, "/auth/tokens")
    return {"token": token.token, "is_admin": token.is_admin, "created_at": token.created_at}

@app.get("/auth/tokens", response_model=List[dict])
async def list_tokens(admin_token: Token = Depends(get_admin_token)):
    """List all tokens"""
    tokens = await auth_service.get_all_tokens()
    await auth_service.log_usage(admin_token.token, "/auth/tokens")
    return [
        {
            "token": token.token,
            "is_admin": token.is_admin,
            "created_at": token.created_at
        }
        for token in tokens
    ]

@app.delete("/auth/tokens/{token_to_delete}")
async def delete_token(
    token_to_delete: str,
    admin_token: Token = Depends(get_admin_token)
):
    """Delete a specific token"""
    success = await auth_service.delete_token(token_to_delete)
    await auth_service.log_usage(admin_token.token, f"/auth/tokens/{token_to_delete}")
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found"
        )
    
    return {"message": "Token deleted successfully"}

# Moderation endpoint
@app.post("/moderate", response_model=ModerationResult)
async def moderate_image(
    file: UploadFile = File(...),
    current_token: Token = Depends(get_current_token)
):
    """Analyze an uploaded image for harmful content"""
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    try:
        # Read and process image
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data))
        
        # Analyze image
        result = await image_analyzer.analyze_image(image)
        
        # Log usage
        await auth_service.log_usage(current_token.token, "/moderate")
        
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing image: {str(e)}"
        )

# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7000)