from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from enum import Enum
from app.models.base import MongoBaseModel, PyObjectId
from bson import ObjectId

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    ANALYST = "analyst"
    PENTESTER = "pentester"

class SubscriptionTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"

class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    disabled: bool = False

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    hashed_password: Optional[str] = None
    is_superuser: bool = False
    scan_limit: int = 10
    pentest_limit: int = 5
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class UserResponse(UserBase):
    id: str
    is_superuser: bool = False
    created_at: datetime

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: str  # user id
    exp: datetime
    type: str  # "access" or "refresh"

class RefreshToken(MongoBaseModel):
    user_id: PyObjectId
    token: str
    expires_at: datetime
    is_blacklisted: bool = False

    class Collection:
        name = "refresh_tokens" 