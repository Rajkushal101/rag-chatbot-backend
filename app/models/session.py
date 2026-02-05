"""Session model."""
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Session(Base):
    """
    Represents a chat session.
    All conversations and documents are scoped to a session.
    """
    __tablename__ = "sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    session_metadata = Column(JSONB, default={})
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    documents = relationship("Document", back_populates="session", cascade="all, delete-orphan")
