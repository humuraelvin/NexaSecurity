from fastapi import APIRouter, Depends, HTTPException, status, Response, Request, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from typing import Optional
import os
from datetime import timedelta

from ..database.database import get_db
from ..schemas.auth import LoginRequest, LoginResponse, SignupRequest, SignupResponse, User, Token, RefreshTokenRequest
from ..services.auth_service import authenticate_user, create_user, generate_token_for_user, generate_tokens_for_user, get_user_by_id
from ..core.security import (
    get_current_user, 
    set_auth_cookies, 
    clear_auth_cookies, 
    SECRET_KEY, 
    ALGORITHM,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    responses={401: {"description": "Unauthorized"}},
)

@router.post("/login/json", response_model=LoginResponse)
async def login_json(login_data: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens
    tokens = generate_tokens_for_user(user)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    # Set cookies for frontend
    set_auth_cookies(response, access_token, refresh_token)
    
    # Convert the SQLAlchemy model to Pydantic model
    user_data = User(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        company_name=user.company_name,
        subscription_tier=user.subscription_tier,
        is_active=user.is_active
    )
    
    # Return token for frontend storage if needed
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data
    )

@router.get("/profile", response_model=User)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's profile information"""
    return current_user

@router.post("/login/token", response_model=Token)
async def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Generate tokens
    tokens = generate_tokens_for_user(user)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    # Set cookies for frontend
    set_auth_cookies(response, access_token, refresh_token)
    
    # Return tokens for API usage
    return Token(
        access_token=access_token, 
        token_type="bearer",
        refresh_token=refresh_token
    )

@router.post("/signup", response_model=SignupResponse)
async def signup(signup_data: SignupRequest, response: Response, db: Session = Depends(get_db)):
    user = create_user(db, signup_data)
    
    # Generate tokens
    tokens = generate_tokens_for_user(user)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    
    # Set cookies for frontend
    set_auth_cookies(response, access_token, refresh_token)
    
    # Convert the SQLAlchemy model to Pydantic model
    user_data = User(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        company_name=user.company_name,
        subscription_tier=user.subscription_tier,
        is_active=user.is_active
    )
    
    # Return user with token
    return SignupResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_data
    )

@router.post("/logout")
async def logout(response: Response, current_user: User = Depends(get_current_user)):
    # Clear cookies for frontend
    clear_auth_cookies(response)
    
    # For stateless JWT, no server-side action needed
    return {"status": "success", "message": "Logged out successfully"}

@router.post("/refresh", response_model=Token)
async def refresh_token(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
    refresh_token_data: RefreshTokenRequest = None,
    refresh_token_cookie: Optional[str] = Cookie(None, alias="refresh_token")
):
    # Get refresh token from request body or cookie
    refresh_token = refresh_token_data.refresh_token if refresh_token_data and refresh_token_data.refresh_token else refresh_token_cookie
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Decode the refresh token
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Get user from database
        user = get_user_by_id(user_id, db)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new access token
        access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
        access_token = create_access_token(
            data={"sub": user_id},
            expires_delta=access_token_expires
        )
        
        # Set new access token cookie
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)) * 60,
            samesite="lax",
            secure=os.getenv("ENVIRONMENT", "development") == "production"
        )
        
        # Return new access token
        return Token(access_token=access_token, token_type="bearer", refresh_token=refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        ) 