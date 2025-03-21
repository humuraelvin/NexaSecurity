from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status, Request, Response
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..schemas.auth import TokenData
from ..database.database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password context for hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login/token", auto_error=False)

def verify_password(plain_password, hashed_password):
    """Verify password with hashed password"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Get hash of password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt

def create_refresh_token(data: dict):
    """Create refresh token with longer expiry"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def set_auth_cookies(response: Response, access_token: str, refresh_token: str = None):
    """Set auth cookies for frontend"""
    # Set access token cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax",
        secure=os.getenv("ENVIRONMENT", "development") == "production"  # Only secure in production
    )
    
    # Set refresh token cookie if provided
    if refresh_token:
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # days to seconds
            samesite="lax",
            secure=os.getenv("ENVIRONMENT", "development") == "production"  # Only secure in production
        )

def clear_auth_cookies(response: Response):
    """Clear auth cookies on logout"""
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

async def get_token_from_cookie_or_header(request: Request, token_from_header: Optional[str] = Depends(oauth2_scheme)):
    """Get token from cookie, localStorage header or Authorization header directly"""
    # Try to get from cookie
    token = request.cookies.get("access_token")
    
    # If not in cookie, use the one from header (oauth2_scheme)
    if not token and token_from_header:
        token = token_from_header
        
    # If still no token, try to extract from Authorization header manually
    # This handles the case when the frontend sends the token as "Bearer <token>"
    if not token and request:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
    return token

async def get_current_user(
    request: Request = None,
    token: Optional[str] = Depends(get_token_from_cookie_or_header),
    db: Session = Depends(get_db)
):
    """Get current user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not token:
        raise credentials_exception
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        
        if user_id is None:
            raise credentials_exception
            
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
        
    # Get user from database using the provided database session
    from ..services.auth_service import get_user_by_id
    user = get_user_by_id(token_data.user_id, db)
    
    if user is None:
        raise credentials_exception
        
    return user 