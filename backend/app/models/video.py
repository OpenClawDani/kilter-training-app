from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Integer
from datetime import datetime
from app.core.database import Base
import uuid


class VideoUpload(Base):
    __tablename__ = "video_uploads"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)

    # Storage
    original_file_path = Column(String, nullable=True)
    filename = Column(String, nullable=True)
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)

    # Processing
    status = Column(String, default="pending")
    processing_status = Column(String, default="pending")

    # Gemini Integration
    gemini_file_id = Column(String(255), nullable=True)
    form_analysis = Column(JSON, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Metadata
    title = Column(String, nullable=True)
    grade_attempted = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<VideoUpload {self.id} - {self.processing_status}>"
