"""
SQLAlchemy Database Models.

Defines 4 tables: workers, violation_logs, compliance_reports, worker_face_embeddings.
"""

import enum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, Index
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class SeverityLevel(enum.Enum):
    """Violation severity levels."""
    LOW = "low"
    MEDIUM = "medium"
    CRITICAL = "critical"


def calculate_severity(missing_count: int) -> str:
    """Calculate violation severity based on number of missing PPE items.

    Args:
        missing_count: Number of missing PPE items (1-5)

    Returns:
        Severity string: "low", "medium", or "critical"
    """
    if missing_count <= 0:
        return SeverityLevel.LOW.value
    elif missing_count == 1:
        return SeverityLevel.LOW.value
    elif missing_count <= 3:
        return SeverityLevel.MEDIUM.value
    else:
        return SeverityLevel.CRITICAL.value


class Worker(Base):
    """Worker registry table."""
    __tablename__ = 'workers'

    worker_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    position = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    date_registered = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, nullable=True)

    violations = relationship('ViolationLog', back_populates='worker')
    face_embeddings = relationship('WorkerFaceEmbedding', back_populates='worker')

    __table_args__ = (
        Index('idx_email', 'email'),
        Index('idx_department', 'department'),
    )


class ViolationLog(Base):
    """PPE violation log table."""
    __tablename__ = 'violation_logs'

    violation_id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(String(50), ForeignKey('workers.worker_id'))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    missing_ppe = Column(Text)           # JSON string: '["helmet","gloves"]'
    image_path = Column(String(255))
    email_sent = Column(Boolean, default=False)
    email_sent_time = Column(DateTime, nullable=True)
    severity = Column(String(10), default='medium')

    worker = relationship('Worker', back_populates='violations')

    __table_args__ = (
        Index('idx_worker_timestamp', 'worker_id', 'timestamp'),
    )


class ComplianceReport(Base):
    """Daily compliance report table."""
    __tablename__ = 'compliance_reports'

    report_id = Column(Integer, primary_key=True, autoincrement=True)
    report_date = Column(DateTime, index=True)
    total_violations = Column(Integer)
    total_workers_checked = Column(Integer)
    compliance_rate = Column(Float)
    critical_violations = Column(Integer)
    medium_violations = Column(Integer)
    low_violations = Column(Integer)


class WorkerFaceEmbedding(Base):
    """Worker face embedding storage table."""
    __tablename__ = 'worker_face_embeddings'

    embedding_id = Column(Integer, primary_key=True, autoincrement=True)
    worker_id = Column(String(50), ForeignKey('workers.worker_id'), index=True)
    embedding_vector = Column(Text)      # JSON-serialized list of 512 floats
    image_path = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    worker = relationship('Worker', back_populates='face_embeddings')
