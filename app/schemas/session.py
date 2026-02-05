"""Pydantic schemas for API requests and responses."""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class SessionCreate(BaseModel):
    """Request schema for creating a session."""
    session_metadata: Optional[dict] = {}


class SessionResponse(BaseModel):
    """Response schema for session."""
    session_id: UUID
    created_at: datetime
    session_metadata: dict

    class Config:
        from_attributes = True
