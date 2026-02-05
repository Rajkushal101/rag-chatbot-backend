"""Document upload routes."""
from fastapi import APIRouter, UploadFile, File, Depends, BackgroundTasks, HTTPException
from uuid import UUID
from app.services.document_service import DocumentService
from app.schemas.document import DocumentResponse
from app.api.dependencies import get_document_service

router = APIRouter(prefix="/upload", tags=["documents"])


@router.post("/{session_id}", response_model=DocumentResponse, status_code=202)
async def upload_document(
    session_id: UUID,
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    doc_service: DocumentService = Depends(get_document_service)
):
    """
    Upload a document for RAG context.
    
    The document will be processed asynchronously:
    1. Parsed (PDF/TXT)
    2. Chunked into sections
    3. Embedded with OpenAI
    4. Stored in pgvector with session metadata
    
    Supported formats: PDF, TXT
    
    Args:
        session_id: Session UUID
        file: Uploaded file
        background_tasks: FastAPI background tasks
        doc_service: Document service dependency
        
    Returns:
        DocumentResponse indicating upload accepted
        
    Raises:
        HTTPException: If file type is unsupported
    """
    # Validate file type
    allowed_types = ["application/pdf", "text/plain"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed: {allowed_types}"
        )
    
    # Read file content
    content = await file.read()
    
    # Schedule background processing
    background_tasks.add_task(
        doc_service.ingest_document,
        file_content=content,
        filename=file.filename,
        session_id=session_id,
        mime_type=file.content_type
    )
    
    return DocumentResponse(
        message="Document upload accepted. Processing in background.",
        filename=file.filename,
        session_id=session_id
    )
