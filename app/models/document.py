"""Document model."""
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.database import Base


class Document(Base):
    """
    Represents uploaded documents.
    status: 'pending', 'processing', 'indexed', 'failed'
    """
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    mime_type = Column(String(100))
    file_size = Column(Integer)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'processing', 'indexed', 'failed')",
            name="valid_status"
        ),
    )
    
    # Relationships
    session = relationship("Session", back_populates="documents")
