from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, func
from typing import Optional, List
import json

from utils.database import get_db
from models.db_models import LogEntry, Analysis, Feedback
from models.schemas import LogUploadResponse, AnalysisResponse, HistoryItem
from services.analysis_service import process_and_analyze, get_analysis_by_id

router = APIRouter(prefix="/logs", tags=["logs"])


@router.post("/upload", response_model=LogUploadResponse)
async def upload_log(
    file: Optional[UploadFile] = File(None),
    raw_log: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    if file:
        content = await file.read()
        log_text = content.decode("utf-8", errors="replace")
        filename = file.filename
    elif raw_log:
        log_text = raw_log
        filename = "pasted_log.txt"
    else:
        raise HTTPException(status_code=400, detail="Provide a file or raw_log text")

    if not log_text.strip():
        raise HTTPException(status_code=400, detail="Log content is empty")

    from utils.log_processor import classify_failure, preprocess_log
    _, category = preprocess_log(log_text)

    from models.db_models import LogEntry
    log_entry = LogEntry(
        filename=filename,
        raw_log=log_text,
        failure_category=category,
    )
    db.add(log_entry)
    await db.commit()
    await db.refresh(log_entry)

    return LogUploadResponse(
        log_entry_id=log_entry.id,
        filename=filename,
        failure_category=category,
        message="Log uploaded successfully. Call /logs/{id}/analyze to process.",
    )


@router.post("/{log_entry_id}/analyze", response_model=AnalysisResponse)
async def analyze_log(
    log_entry_id: int,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(LogEntry).where(LogEntry.id == log_entry_id))
    log_entry = result.scalar_one_or_none()

    if not log_entry:
        raise HTTPException(status_code=404, detail="Log entry not found")

    # Check if already analyzed
    existing = await db.execute(
        select(Analysis).where(Analysis.log_entry_id == log_entry_id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Already analyzed. Fetch from /analyses/{id}")

    analysis = await process_and_analyze(db, log_entry.raw_log, log_entry.filename)
    return analysis


@router.post("/upload-and-analyze", response_model=AnalysisResponse)
async def upload_and_analyze(
    file: Optional[UploadFile] = File(None),
    raw_log: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Single endpoint: upload + analyze in one call."""
    if file:
        content = await file.read()
        log_text = content.decode("utf-8", errors="replace")
        filename = file.filename
    elif raw_log:
        log_text = raw_log
        filename = "pasted_log.txt"
    else:
        raise HTTPException(status_code=400, detail="Provide a file or raw_log text")

    if not log_text.strip():
        raise HTTPException(status_code=400, detail="Log content is empty")

    return await process_and_analyze(db, log_text, filename)


@router.get("/history", response_model=List[HistoryItem])
async def get_history(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(LogEntry, Analysis)
        .join(Analysis, LogEntry.id == Analysis.log_entry_id)
        .order_by(desc(Analysis.created_at))
        .offset(skip)
        .limit(limit)
    )
    rows = await db.execute(stmt)
    pairs = rows.fetchall()

    history = []
    for log_entry, analysis in pairs:
        # Count feedbacks
        fb_result = await db.execute(
            select(func.count(Feedback.id)).where(Feedback.analysis_id == analysis.id)
        )
        total_fb = fb_result.scalar() or 0

        correct_fb_result = await db.execute(
            select(func.count(Feedback.id)).where(
                Feedback.analysis_id == analysis.id,
                Feedback.is_correct == True,
            )
        )
        correct_fb = correct_fb_result.scalar() or 0

        history.append(
            HistoryItem(
                log_entry_id=log_entry.id,
                analysis_id=analysis.id,
                filename=log_entry.filename,
                failure_category=log_entry.failure_category or "unknown",
                summary=analysis.summary or "",
                root_cause=analysis.root_cause or "",
                created_at=analysis.created_at,
                feedback_count=total_fb,
                correct_feedback_count=correct_fb,
            )
        )
    return history
