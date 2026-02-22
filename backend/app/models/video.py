from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float, Integer
from datetime import datetime
from app.core.database import Base
import uuid


class VideoUpload(Base):
    __tablename__ = "video_uploads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Storage
    original_file_path = Column(String, nullable=False)
    fragment_file_path = Column(String, nullable=True)

    # Processing
    status = Column(String, default="pending")  # pending / processing / completed / failed

    # Gemini Analysis Results
    form_feedback = Column(String, nullable=True)
    grade_estimate = Column(String, nullable=True)
    body_position = Column(JSON, nullable=True)
    holds_analysis = Column(JSON, nullable=True)
    key_weaknesses = Column(JSON, nullable=True)

    # Fragment settings
    fragment_start = Column(Float, nullable=True)
    fragment_end = Column(Float, nullable=True)

    # Metadata
    notes = Column(String, nullable=True)
    duration = Column(Float, nullable=True)
    file_size = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        kwargs.setdefault("status", "pending")
        super().__init__(**kwargs)

    def __repr__(self):
        return f"<VideoUpload {self.id} - {self.status}>"
