"""Vector store repository for pgvector operations.

This module handles all interactions with the pgvector database for
storing and retrieving document embeddings with session isolation.
"""
import logging
from typing import List
from uuid import UUID
from langchain_community.vectorstores import PGVector
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from app.config import settings

logger = logging.getLogger(__name__)


class VectorStoreRepository:
    """
    Handles all vector database operations with pgvector.
    Enforces session-based isolation for security.
    """
    
    def __init__(self):
        """Initialize the vector store with OpenAI embeddings."""
        self.embeddings = OpenAIEmbeddings(
            model=settings.EMBEDDING_MODEL,
            openai_api_key=settings.OPENAI_API_KEY
        )
        
        self.vector_store = PGVector(
            connection_string=settings.DATABASE_URL.replace('+asyncpg', ''),  # PGVector uses psycopg2
            embedding_function=self.embeddings,
            collection_name="documents",
            distance_strategy="cosine"
        )
    
    async def add_documents(self, documents: List[Document]) -> None:
        """
        Add documents to the vector store.
        Each document MUST have session_id in metadata.
        
        Args:
            documents: List of LangChain Document objects with metadata
            
        Raises:
            ValueError: If session_id missing from any document metadata
        """
        # Validate session_id exists in metadata
        for doc in documents:
            if "session_id" not in doc.metadata:
                raise ValueError(
                    f"session_id required in document metadata. "
                    f"Got metadata: {doc.metadata}"
                )
        
        logger.info(f"Adding {len(documents)} documents to vector store")
        await self.vector_store.aadd_documents(documents)
        logger.info(f"Successfully added {len(documents)} documents")
    
    async def similarity_search(
        self,
        query: str,
        session_id: UUID,
        k: int = 4
    ) -> List[Document]:
        """
        ⭐ CRITICAL: Search with session isolation.
        Only retrieve documents from the specified session.
        
        This method filters vectors by session_id BEFORE performing
        similarity search, preventing data leakage between sessions.
        
        Args:
            query: The search query
            session_id: Session UUID for filtering
            k: Number of results to return
            
        Returns:
            List of most similar documents from this session only
        """
        # Build metadata filter - CRITICAL for session isolation
        filter_dict = {"session_id": str(session_id)}
        
        logger.info(f"Searching vectors for session {session_id} with query: {query[:50]}...")
        
        try:
            # Perform filtered search - filter BEFORE vector search
            results = await self.vector_store.asimilarity_search(
                query=query,
                k=k,
                filter=filter_dict  # ⭐ Pre-filter before vector search
            )
            
            logger.info(f"Found {len(results)} results for session {session_id}")
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed for session {session_id}: {e}")
            # Return empty list on failure (graceful degradation)
            return []
