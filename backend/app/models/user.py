"""SQLAlchemy models for authentication-related persistence."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from app.database.database import Base


class User(Base):
    """Persist application users with unique credentials and audit metadata."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)