from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
import json

from utils.database import get_db
from models.db_models import LogEntry, Analysis, Feedback
from models.schemas import MetricsResponse

router = APIRouter(prefix="/metrics", tags=["metrics"])


@router.get("/", response_model=MetricsResponse)
async def get_metrics(db: AsyncSession = Depends(get_db)):
    # Total analyses
    total_result = await db.execute(select(func.count(Analysis.id)))
    total = total_result.scalar() or 0

    # Feedback accuracy
    total_fb_result = await db.execute(select(func.count(Feedback.id)))
    total_fb = total_fb_result.scalar() or 0

    correct_fb_result = await db.execute(
        select(func.count(Feedback.id)).where(Feedback.is_correct == True)
    )
    correct_fb = correct_fb_result.scalar() or 0
    accuracy = round(correct_fb / total_fb, 3) if total_fb > 0 else 0.0

    # Failure category breakdown
    breakdown_result = await db.execute(
        select(LogEntry.failure_category, func.count(LogEntry.id))
        .join(Analysis, LogEntry.id == Analysis.log_entry_id)
        .group_by(LogEntry.failure_category)
    )
    failure_breakdown = {row[0] or "unknown": row[1] for row in breakdown_result.fetchall()}

    # Weekly trend (last 7 days)
    weekly = []
    for i in range(6, -1, -1):
        day = datetime.utcnow() - timedelta(days=i)
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        cnt_result = await db.execute(
            select(func.count(Analysis.id)).where(
                and_(Analysis.created_at >= start, Analysis.created_at < end)
            )
        )
        weekly.append({
            "date": start.strftime("%Y-%m-%d"),
            "count": cnt_result.scalar() or 0,
        })

    # Top root causes (word frequency approximation)
    rc_result = await db.execute(select(Analysis.root_cause).limit(200))
    root_causes_raw = [row[0] for row in rc_result.fetchall() if row[0]]
    word_freq: dict = {}
    for rc in root_causes_raw:
        for word in rc.lower().split():
            if len(word) > 5:
                word_freq[word] = word_freq.get(word, 0) + 1
    top_causes = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    top_root_causes = [{"term": t, "count": c} for t, c in top_causes]

    # Avg fixes per analysis
    fixes_result = await db.execute(select(Analysis.suggested_fixes).limit(100))
    counts = []
    for row in fixes_result.fetchall():
        try:
            counts.append(len(json.loads(row[0] or "[]")))
        except Exception:
            pass
    avg_fixes = round(sum(counts) / len(counts), 2) if counts else 0.0

    return MetricsResponse(
        total_analyses=total,
        accuracy_rate=accuracy,
        failure_breakdown=failure_breakdown,
        weekly_trend=weekly,
        top_root_causes=top_root_causes,
        avg_fixes_per_analysis=avg_fixes,
    )
