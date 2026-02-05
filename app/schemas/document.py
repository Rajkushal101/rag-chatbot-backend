"""Pydantic schemas for document functionality."""
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class DocumentResponse(BaseModel):
    """Response schema for document upload."""
    message: str
    filename: str
    session_id: UUID
    document_id: Optional[UUID] = None
