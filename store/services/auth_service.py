from datetime import datetime, timezone
from bson import ObjectId
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient

from store.models.user.user_model import UserCreate
from store.models.auth.auth_model import PasswordReset, TokenResponse, UserLogin
from store.utils.util import get_hashed_password, verify_hashed_password, generate_tokens

class AuthService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.user_collection = self.db.user

    async def login_user(self, user_credentials: UserLogin) -> TokenResponse:
        """Authenticate user and generate tokens"""
        username = user_credentials.username.lower()
        user_data = await self.user_collection.find_one({"username": username})
        
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if not verify_hashed_password(user_credentials.password, user_data["password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        
        user_id = str(user_data["_id"])
        return generate_tokens(user_id)

    async def refresh_tokens(self, user_id: str) -> TokenResponse:
        """Generate new tokens using refresh token"""
        user_data = await self.user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return generate_tokens(user_id)

    async def register_user(self, user_data: UserCreate) -> TokenResponse:
        """Register a new user and return tokens"""
        # Check if username already exists
        existing_user = await self.user_collection.find_one({
            "$or": [
                {"username": user_data.username.lower()},
                {"email": user_data.email.lower()}
            ]
        })
        
        if existing_user:
            if existing_user["username"] == user_data.username.lower():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
            else:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        
        # Create new user
        hashed_password = get_hashed_password(user_data.password)
        new_user = {
            "username": user_data.username.lower(),
            "email": user_data.email.lower(),
            "password": hashed_password,
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "review_count": 0,
            "recent_reviews": []
        }
        
        result = await self.user_collection.insert_one(new_user)
        user_id = str(result.inserted_id)
        
        return generate_tokens(user_id)

    async def reset_password(self, user_id: str, password_data: PasswordReset) -> JSONResponse:
        """Reset user password"""
        user_data = await self.user_collection.find_one({"_id": ObjectId(user_id)})
        
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        # If old password is provided, verify it
        if password_data.old_password:
            if not verify_hashed_password(password_data.old_password, user_data["password"]):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Current password is incorrect")
        
        # Update password
        hashed_password = get_hashed_password(password_data.new_password)
        await self.user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": hashed_password, "updated_at": datetime.now(timezone.utc)}}
        )
        
        return JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Password updated successfully"})