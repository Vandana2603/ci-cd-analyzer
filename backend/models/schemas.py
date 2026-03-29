from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class LogUploadResponse(BaseModel):
    log_entry_id: int
    filename: Optional[str]
    failure_category: str
    message: str


class SimilarIssue(BaseModel):
    log_entry_id: int
    summary: str
    root_cause: str
    fixes: List[str]
    similarity_score: float
    feedback_score: Optional[float] = None


class AnalysisResponse(BaseModel):
    analysis_id: int
    log_entry_id: int
    failure_category: str
    summary: str
    root_cause: str
    suggested_fixes: List[str]
    similar_issues: List[SimilarIssue]
    created_at: datetime

    class Config:
        from_attributes = True


class FeedbackRequest(BaseModel):
    analysis_id: int
    is_correct: bool
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    feedback_id: int
    analysis_id: int
    is_correct: bool
    message: str


class HistoryItem(BaseModel):
    log_entry_id: int
    analysis_id: int
    filename: Optional[str]
    failure_category: str
    summary: str
    root_cause: str
    created_at: datetime
    feedback_count: int
    correct_feedback_count: int

    class Config:
        from_attributes = True


class MetricsResponse(BaseModel):
    total_analyses: int
    accuracy_rate: float
    failure_breakdown: dict
    weekly_trend: List[dict]
    top_root_causes: List[dict]
    avg_fixes_per_analysis: float
