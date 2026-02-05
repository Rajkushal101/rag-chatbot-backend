"""Document repository for managing uploaded documents."""
import logging
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Handles database operations for documents."""
    
    def __init__(self, db: AsyncSession):
        """
        Initialize document repository.
        
        Args:
            db: Async SQLAlchemy session
        """
        self.db = db
    
    async def create_document(
        self,
        session_id: UUID,
        filename: str,
        mime_type: str,
        file_size: int = 0
    ) -> Document:
        """
        Create a new document record.
        
        Args:
            session_id: Session UUID
            filename: Original filename
            mime_type: MIME type
            file_size: File size in bytes
            
        Returns:
            Created Document instance
        """
        document = Document(
            session_id=session_id,
            filename=filename,
            mime_type=mime_type,
            file_size=file_size,
            status="pending"
        )
        
        self.db.add(document)
        await self.db.flush()
        
        logger.info(f"Created document record: {filename} for session {session_id}")
        return document
    
    async def update_status(
        self,
        document_id: UUID,
        status: str
    ) -> None:
        """
        Update document processing status.
        
        Args:
            document_id: Document UUID
            status: New status ('pending', 'processing', 'indexed', 'failed')
        """
        from sqlalchemy import select, update
        
        stmt = (
            update(Document)
            .where(Document.id == document_id)
            .values(status=status)
        )
        
        await self.db.execute(stmt)
        await self.db.flush()
        
        logger.info(f"Updated document {document_id} status to: {status}")
