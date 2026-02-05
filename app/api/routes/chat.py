"""Chat routes."""
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
from app.services.chat_service import ChatService
from app.schemas.chat import ChatRequest, ChatResponse
from app.api.dependencies import get_chat_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/{session_id}", response_model=ChatResponse)
async def chat(
    session_id: UUID,
    request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service)
):
    """
    Send a message and get AI response with RAG.
    
    The AI will:
    1. Retrieve relevant context from uploaded documents (session-filtered)
    2. Use conversation history for continuity
    3. Generate a contextual response
    
    Args:
        session_id: Session UUID
        request: Chat request with user message
        chat_service: Chat service dependency
        
    Returns:
        ChatResponse with assistant's message
        
    Raises:
        HTTPException: If chat generation fails
    """
    try:
        response_message = await chat_service.generate_response(
            session_id=session_id,
            user_message=request.message
        )
        
        return ChatResponse(
            session_id=session_id,
            message=response_message
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat generation failed: {str(e)}"
        )
