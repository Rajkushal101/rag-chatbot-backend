"""Chat message model."""
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class ChatMessage(Base):
    """
    Stores individual chat messages.
    role: 'user', 'assistant', or 'system'
    """
    __tablename__ = "chat_messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="valid_role"),
    )
    
    # Relationships
    session = relationship("Session", back_populates="messages")
