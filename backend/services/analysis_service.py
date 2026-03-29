import json
import uuid
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from models.db_models import LogEntry, Analysis, Feedback
from models.schemas import AnalysisResponse, SimilarIssue
from utils.log_processor import preprocess_log
from services.vector_store import get_vector_store
from services.llm_service import analyze_with_llm
from config import settings


async def process_and_analyze(
    db: AsyncSession,
    raw_log: str,
    filename: Optional[str] = None,
) -> AnalysisResponse:
    """Full pipeline: preprocess → retrieve similar → LLM → store → return."""

    # 1. Preprocess
    preprocessed, category = preprocess_log(raw_log)

    # 2. Store log entry
    log_entry = LogEntry(
        filename=filename,
        raw_log=raw_log,
        preprocessed_log=preprocessed,
        failure_category=category,
    )
    db.add(log_entry)
    await db.flush()  # get the id

    # 3. RAG: retrieve similar past issues
    vs = get_vector_store()
    similar_raw = vs.query_similar(preprocessed, top_k=settings.TOP_K_SIMILAR)

    # 4. LLM analysis
    llm_result = await analyze_with_llm(preprocessed, category, similar_raw)

    summary = llm_result.get("summary", "")
    root_cause = llm_result.get("root_cause", "")
    fixes = llm_result.get("suggested_fixes", [])

    # 5. Store in ChromaDB for future RAG
    doc_id = str(uuid.uuid4())
    vs.add_document(
        doc_id=doc_id,
        text=preprocessed,
        metadata={
            "log_entry_id": log_entry.id,
            "failure_category": category,
            "summary": summary[:500],
            "root_cause": root_cause[:300],
            "fixes_preview": "; ".join(fixes[:2])[:400],
            "feedback_score": 0.0,
        },
    )

    # 6. Build similar_issues list
    similar_issues = []
    for item in similar_raw:
        meta = item.get("metadata", {})
        log_id = int(meta.get("log_entry_id", 0))
        if log_id == log_entry.id:
            continue  # skip self

        # Fetch feedback-adjusted score
        fb_score = float(meta.get("feedback_score", 0.0))

        fixes_preview = meta.get("fixes_preview", "")
        fix_list = [f.strip() for f in fixes_preview.split(";") if f.strip()] if fixes_preview else []

        similar_issues.append(
            SimilarIssue(
                log_entry_id=log_id,
                summary=meta.get("summary", "N/A"),
                root_cause=meta.get("root_cause", "N/A"),
                fixes=fix_list,
                similarity_score=item.get("similarity", 0.0),
                feedback_score=fb_score,
            )
        )

    # 7. Store analysis in DB
    analysis = Analysis(
        log_entry_id=log_entry.id,
        summary=summary,
        root_cause=root_cause,
        suggested_fixes=json.dumps(fixes),
        similar_issues=json.dumps([s.model_dump() for s in similar_issues]),
        chroma_doc_id=doc_id,
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)
    await db.refresh(log_entry)

    return AnalysisResponse(
        analysis_id=analysis.id,
        log_entry_id=log_entry.id,
        failure_category=category,
        summary=summary,
        root_cause=root_cause,
        suggested_fixes=fixes,
        similar_issues=similar_issues,
        created_at=analysis.created_at,
    )


async def get_analysis_by_id(db: AsyncSession, analysis_id: int) -> Optional[AnalysisResponse]:
    result = await db.execute(
        select(Analysis).where(Analysis.id == analysis_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        return None

    log_entry_result = await db.execute(
        select(LogEntry).where(LogEntry.id == analysis.log_entry_id)
    )
    log_entry = log_entry_result.scalar_one_or_none()

    fixes = json.loads(analysis.suggested_fixes or "[]")
    similar = json.loads(analysis.similar_issues or "[]")

    return AnalysisResponse(
        analysis_id=analysis.id,
        log_entry_id=analysis.log_entry_id,
        failure_category=log_entry.failure_category if log_entry else "unknown",
        summary=analysis.summary or "",
        root_cause=analysis.root_cause or "",
        suggested_fixes=fixes,
        similar_issues=[SimilarIssue(**s) for s in similar],
        created_at=analysis.created_at,
    )
