"""Session management routes."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.session import Session as SessionModel
from app.schemas.session import SessionCreate, SessionResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
async def create_session(
    session_data: SessionCreate = SessionCreate(),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new chat session.
    
    Returns a unique session_id that should be used for all
    subsequent uploads and chat requests.
    
    Returns:
        SessionResponse with session_id and metadata
    """
    # Create new session
    session = SessionModel(session_metadata=session_data.session_metadata)
    db.add(session)
    await db.flush()
    
    return SessionResponse(
        session_id=session.id,
        created_at=session.created_at,
        session_metadata=session.session_metadata
    )
