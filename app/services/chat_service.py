"""Chat service with RAG (Retrieval-Augmented Generation).

Handles:
1. Retrieving chat history
2. Filtering vectors by session_id
3. Retrieving relevant context
4. Generating responses with LLM
5. Saving conversation
"""
import logging
from typing import List, Dict
from uuid import UUID
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
from app.repositories.chat_repository import ChatRepository
from app.repositories.vector_store import VectorStoreRepository
from app.config import settings

logger = logging.getLogger(__name__)


class ChatService:
    """
    Handles chat with RAG and conversation history.
    Implements graceful degradation if retrieval fails.
    """
    
    def __init__(
        self,
        chat_repo: ChatRepository,
        vector_repo: VectorStoreRepository
    ):
        """
        Initialize chat service.
        
        Args:
            chat_repo: Chat repository
            vector_repo: Vector store repository
        """
        self.chat_repo = chat_repo
        self.vector_repo = vector_repo
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.LLM_MODEL,
            temperature=0.7,
            api_key=settings.OPENAI_API_KEY
        )
    
    async def generate_response(
        self,
        session_id: UUID,
        user_message: str
    ) -> str:
        """
        Generate a response using RAG and chat history.
        
        Flow:
        1. Save user message
        2. Retrieve chat history (last 10 messages)
        3. Retrieve context with session filtering (CRITICAL)
        4. Build prompt with history + context + message
        5. Generate response with LLM
        6. Save assistant response
        7. Return response
        
        Args:
            session_id: Session UUID
            user_message: User's message
            
        Returns:
            Assistant's response
        """
        try:
            # 1. Save user message
            await self.chat_repo.add_message(
                session_id=session_id,
                role="user",
                content=user_message
            )
            
            # 2. Retrieve chat history for context
            history = await self.chat_repo.get_history(
                session_id=session_id,
                limit=10  # Last 10 messages
            )
            
            # 3. ⭐ CRITICAL: Retrieve context with session filtering
            relevant_docs = await self.vector_repo.similarity_search(
                query=user_message,
                session_id=session_id,  # Filter by session
                k=4  # Top 4 most relevant chunks
            )
            
            # 4. Build context from retrieved documents
            context = "\n\n".join([doc.page_content for doc in relevant_docs]) if relevant_docs else ""
            
            # 5. Build messages for LLM
            messages = self._build_messages(
                user_message=user_message,
                context=context,
                history=history
            )
            
            # 6. Generate response
            logger.info(f"Generating response for session {session_id}")
            response = await self.llm.ainvoke(messages)
            assistant_message = response.content
            
            # 7. Save assistant response
            await self.chat_repo.add_message(
                session_id=session_id,
                role="assistant",
                content=assistant_message
            )
            
            logger.info(f"Generated response for session {session_id}")
            return assistant_message
            
        except Exception as e:
            logger.error(f"Chat generation failed for session {session_id}: {e}")
            # Graceful degradation: respond without RAG
            return await self._fallback_response(user_message)
    
    def _build_messages(
        self,
        user_message: str,
        context: str,
        history: List[Dict]
    ) -> List:
        """
        Build the LLM messages with context and history.
        
        Args:
            user_message: Current user message
            context: Retrieved document context
            history: Conversation history
            
        Returns:
            List of LangChain message objects
        """
        messages = []
        
        # System message with context
        if context:
            system_content = f"""You are a helpful AI assistant. Use the following context from uploaded documents to answer the user's question accurately.

Context from documents:
{context}

Instructions:
- Answer based on the provided context when relevant
- If the context doesn't contain the answer, say so
- Be concise and helpful
- Maintain conversation continuity"""
        else:
            system_content = "You are a helpful AI assistant. Answer the user's questions concisely and accurately."
        
        messages.append(SystemMessage(content=system_content))
        
        # Add conversation history (last 3 exchanges = 6 messages)
        for msg in history[-6:]:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                messages.append(AIMessage(content=msg['content']))
        
        # Add current user message
        messages.append(HumanMessage(content=user_message))
        
        return messages
    
    async def _fallback_response(self, message: str) -> str:
        """
        Fallback response without RAG if retrieval fails.
        
        Args:
            message: User message
            
        Returns:
            LLM response without context
        """
        logger.warning("Using fallback response without RAG")
        
        try:
            messages = [
                SystemMessage(content="You are a helpful assistant."),
                HumanMessage(content=message)
            ]
            
            response = await self.llm.ainvoke(messages)
            return response.content
            
        except Exception as e:
            logger.error(f"Fallback response also failed: {e}")
            return "I apologize, but I'm having trouble processing your request right now. Please try again later."
