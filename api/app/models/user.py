from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.sql import func
import uuid
from ..database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    password = Column(String)
    full_name = Column(String)
    company_name = Column(String, nullable=True)
    subscription_tier = Column(String, default="basic")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 