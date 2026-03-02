from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class VideoUploadCreate(BaseModel):
    notes: Optional[str] = None


class VideoUploadResponse(BaseModel):
    id: str
    status: str
    original_file_path: str
    fragment_file_path: Optional[str] = None
    fragment_start: Optional[float] = None
    fragment_end: Optional[float] = None
    form_feedback: Optional[str] = None
    grade_estimate: Optional[str] = None
    body_position: Optional[dict] = None
    holds_analysis: Optional[list] = None
    key_weaknesses: Optional[list] = None
    notes: Optional[str] = None
    duration: Optional[float] = None
    file_size: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FragmentRequest(BaseModel):
    fragment_start: float
    fragment_end: float

    class Config:
        json_schema_extra = {
            "example": {
                "fragment_start": 5.0,
                "fragment_end": 25.0
            }
        }


class AnalysisResponse(BaseModel):
    form_feedback: str
    grade_estimate: Optional[str] = None
    body_position: dict
    holds_analysis: list
    key_weaknesses: list
