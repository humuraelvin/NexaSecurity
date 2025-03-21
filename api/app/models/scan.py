from sqlalchemy import Column, String, DateTime, JSON, Integer, Float, ForeignKey
from sqlalchemy.sql import func
import uuid
from ..database.database import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"))
    target = Column(String)
    scan_type = Column(String)
    status = Column(String, default="pending")
    progress = Column(Integer, default=0)
    current_task = Column(String, default="Initializing")
    start_time = Column(DateTime, default=func.now())
    end_time = Column(DateTime, nullable=True)
    findings = Column(JSON, default=list)
    summary = Column(JSON, default=dict)
    output_directory = Column(String)
    estimated_time_remaining = Column(Integer, nullable=True) 