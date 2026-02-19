from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from app.core.database import Base
import uuid


class VideoUpload(Base):
    __tablename__ = "video_uploads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    file_path = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending, processing, success, failed
    detected_holds = Column(JSON, nullable=True)  # Array of holds
    detected_circuit_id = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)
    analysis_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<VideoUpload {self.id} - {self.status}>"
