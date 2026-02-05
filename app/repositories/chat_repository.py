"""Chat repository for managing conversation history."""
import logging
from typing import List, Dict
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import ChatMessage

logger = logging.getLogger(__name__)


class ChatRepository:
    """Handles database operations for chat messages."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize chat repository.
        
        Args:
            db: Async SQLAlchemy session
        """
        self.db = db
    
    async def add_message(
        self,
        session_id: UUID,
        role: str,
        content: str
    ) -> ChatMessage:
        """
        Save a message to the database.
        
        Args:
            session_id: Session UUID
            role: Message role ('user', 'assistant', 'system')
            content: Message content
            
        Returns:
            Created ChatMessage instance
        """
        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content
        )
        
        self.db.add(message)
        await self.db.flush()
        
        logger.info(f"Saved {role} message to session {session_id}")
        return message
    
    async def get_history(
        self,
        session_id: UUID,
        limit: int = 10
    ) -> List[Dict]:
        """
        Retrieve chat history for a session.
        
        Args:
            session_id: Session UUID
            limit: Maximum number of messages to retrieve
            
        Returns:
            List of message dictionaries ordered by creation time
        """
        stmt = (
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.desc())
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        messages = result.scalars().all()
        
        # Reverse to get chronological order
        messages = list(reversed(messages))
        
        return [
            {
                "role": msg.role,
                "content": msg.content,
                "created_at": msg.created_at
            }
            for msg in messages
        ]
