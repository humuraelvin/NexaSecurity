from ..models.user import User
from ..core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import uuid
from fastapi import HTTPException, status, Response
from ..database.database import get_db

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_user_by_id(user_id: str, db: Session = None):
    # Always require a database session for user lookups
    if not db:
        # Get a new database session if none was provided
        from ..database.database import SessionLocal
        db = SessionLocal()
        try:
            return db.query(User).filter(User.id == user_id).first()
        finally:
            db.close()
    else:
        return db.query(User).filter(User.id == user_id).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

def create_user(db: Session, user_data):
    # Check if user with this email already exists
    db_user = get_user_by_email(db, user_data.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user with hashed password
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        password=hashed_password,
        full_name=user_data.name,
        company_name=user_data.company,
        subscription_tier=user_data.plan or "basic",
        is_active=True
    )
    
    # Add to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

def generate_tokens_for_user(user):
    """Generate both access and refresh tokens for a user"""
    # Create access token with shorter expiry
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    # Create refresh token with longer expiry
    refresh_token = create_refresh_token(
        data={"sub": user.id}
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def generate_token_for_user(user):
    """Legacy function for backwards compatibility"""
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)))
    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    return access_token