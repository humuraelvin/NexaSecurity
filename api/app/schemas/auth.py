from pydantic import BaseModel, EmailStr
from typing import Optional

class TokenData(BaseModel):
    user_id: str

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: Optional[str] = None

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    subscription_tier: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    
    class Config:
        from_attributes = True  # Updated from orm_mode in Pydantic v2

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    user: User

class SignupRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    company: Optional[str] = None
    plan: Optional[str] = "basic"

class SignupResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    user: User

class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = None 