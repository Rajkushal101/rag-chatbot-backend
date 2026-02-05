"""Document ingestion service.

Handles the complete pipeline for processing uploaded documents:
1. Parse file (PDF/TXT)
2. Chunk text
3. Generate embeddings
4. Store in pgvector with session metadata
"""
import logging
import tempfile
import os
from typing import BinaryIO
from uuid import UUID
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from app.repositories.vector_store import VectorStoreRepository
from app.repositories.document_repository import DocumentRepository
from app.config import settings

logger = logging.getLogger(__name__)


class DocumentService:
    """
    Handles document ingestion pipeline with proper error handling
    and status tracking.
    """
    
    def __init__(
        self,
        vector_repo: VectorStoreRepository,
        doc_repo: DocumentRepository
    ):
        """
        Initialize document service.
        
        Args:
            vector_repo: Vector store repository
            doc_repo: Document repository
        """
        self.vector_repo = vector_repo
        self.doc_repo = doc_repo
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
    
    async def ingest_document(
        self,
        file_content: bytes,
        filename: str,
        session_id: UUID,
        mime_type: str
    ) -> UUID:
        """
        Ingest a document into the vector store.
        
        Processing pipeline:
        1. Create document record (status='pending')
        2. Parse file based on MIME type
        3. Chunk text with overlap
        4. Add session_id to every chunk's metadata (CRITICAL)
        5. Generate embeddings and store in pgvector
        6. Update status to 'indexed' or 'failed'
        
        Args:
            file_content: Binary file content
            filename: Original filename
            session_id: Session UUID for isolation
            mime_type: MIME type of the file
            
        Returns:
            Document UUID
            
        Raises:
            ValueError: For unsupported file types
        """
        document = None
        temp_file_path = None
        
        try:
            # 1. Create document record
            document = await self.doc_repo.create_document(
                session_id=session_id,
                filename=filename,
                mime_type=mime_type,
                file_size=len(file_content)
            )
            
            logger.info(f"Processing document {document.id}: {filename}")
            
            # 2. Update status to processing
            await self.doc_repo.update_status(document.id, "processing")
            
            # 3. Write to temporary file (loaders need file paths)
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
                temp_file.write(file_content)
                temp_file_path = temp_file.name
            
            # 4. Load document based on type
            if mime_type == "application/pdf":
                loader = PyPDFLoader(temp_file_path)
            elif mime_type in ["text/plain", "text/markdown"]:
                loader = TextLoader(temp_file_path)
            else:
                raise ValueError(f"Unsupported file type: {mime_type}")
            
            documents = loader.load()
            logger.info(f"Loaded {len(documents)} pages/sections from {filename}")
            
            # 5. Chunk the documents
            chunks = self.text_splitter.split_documents(documents)
            logger.info(f"Split into {len(chunks)} chunks")
            
            # 6. Add metadata to EVERY chunk (CRITICAL for session isolation)
            for chunk in chunks:
                chunk.metadata.update({
                    "session_id": str(session_id),  # ⭐ CRITICAL
                    "document_id": str(document.id),
                    "filename": filename
                })
            
            # 7. Store in vector database
            await self.vector_repo.add_documents(chunks)
            
            # 8. Update document status to indexed
            await self.doc_repo.update_status(document.id, "indexed")
            
            logger.info(f"Successfully ingested {len(chunks)} chunks from {filename}")
            return document.id
            
        except Exception as e:
            logger.error(f"Document ingestion failed for {filename}: {e}")
            if document:
                await self.doc_repo.update_status(document.id, "failed")
            raise
            
        finally:
            # Clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logger.warning(f"Failed to delete temp file: {e}")
