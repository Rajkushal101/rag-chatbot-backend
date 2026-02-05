"""Pydantic schemas for chat functionality."""
from pydantic import BaseModel
from uuid import UUID


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    message: str


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    session_id: UUID
    message: str
