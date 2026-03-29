from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=True)
    raw_log = Column(Text, nullable=False)
    preprocessed_log = Column(Text, nullable=True)
    failure_category = Column(String(50), nullable=True)  # build, test, infrastructure
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="log_entry", uselist=False)


class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    log_entry_id = Column(Integer, ForeignKey("log_entries.id"), nullable=False)
    summary = Column(Text, nullable=True)
    root_cause = Column(Text, nullable=True)
    suggested_fixes = Column(Text, nullable=True)  # JSON string
    similar_issues = Column(Text, nullable=True)   # JSON string
    chroma_doc_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    log_entry = relationship("LogEntry", back_populates="analysis")
    feedbacks = relationship("Feedback", back_populates="analysis")


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"), nullable=False)
    is_correct = Column(Boolean, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="feedbacks")
