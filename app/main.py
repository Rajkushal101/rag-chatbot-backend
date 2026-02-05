"""FastAPI main application."""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import session, upload, chat
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="RAG Chatbot Backend",
    description="Production-grade RAG chatbot with session isolation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (configure as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(session.router)
app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        Status message
    """
    return {
        "status": "healthy",
        "service": "rag-chatbot-backend",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "RAG Chatbot Backend API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )
