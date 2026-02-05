"""Dependency injection for FastAPI routes."""
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.repositories.vector_store import VectorStoreRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.document_repository import DocumentRepository
from app.services.document_service import DocumentService
from app.services.chat_service import ChatService


# Singleton instances
_vector_repo = None


def get_vector_repo() -> VectorStoreRepository:
    """Get or create vector repository singleton."""
    global _vector_repo
    if _vector_repo is None:
        _vector_repo = VectorStoreRepository()
    return _vector_repo


async def get_document_service(db: AsyncSession = get_db) -> DocumentService:
    """
    Get document service with dependencies.
    
    Args:
        db: Database session from dependency
        
    Returns:
        DocumentService instance
    """
    vector_repo = get_vector_repo()
    doc_repo = DocumentRepository(db)
    return DocumentService(vector_repo, doc_repo)


async def get_chat_service(db: AsyncSession = get_db) -> ChatService:
    """
    Get chat service with dependencies.
    
    Args:
        db: Database session from dependency
        
    Returns:
        ChatService instance
    """
    vector_repo = get_vector_repo()
    chat_repo = ChatRepository(db)
    return ChatService(chat_repo, vector_repo)
