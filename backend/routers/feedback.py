from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from utils.database import get_db
from models.db_models import Feedback, Analysis
from models.schemas import FeedbackRequest, FeedbackResponse
from services.vector_store import get_vector_store

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    request: FeedbackRequest,
    db: AsyncSession = Depends(get_db),
):
    # Validate analysis exists
    result = await db.execute(
        select(Analysis).where(Analysis.id == request.analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # Store feedback
    feedback = Feedback(
        analysis_id=request.analysis_id,
        is_correct=request.is_correct,
        comment=request.comment,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)

    # Update vector store feedback score
    if analysis.chroma_doc_id:
        vs = get_vector_store()
        delta = 0.1 if request.is_correct else -0.1
        vs.update_feedback_score(analysis.chroma_doc_id, delta)

    return FeedbackResponse(
        feedback_id=feedback.id,
        analysis_id=request.analysis_id,
        is_correct=request.is_correct,
        message="Feedback recorded. Thank you!",
    )
