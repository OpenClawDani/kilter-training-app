"""
Pydantic v2 schemas for video upload and analysis responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class VideoUploadRequest(BaseModel):
    """
    Optional metadata that can accompany a video upload (as form fields).
    The actual file is handled via multipart/form-data, not JSON body.
    """

    model_config = ConfigDict(extra="ignore")

    title: str | None = Field(
        default=None,
        max_length=200,
        description="Optional human-readable title for this climb attempt.",
        examples=["Red problem V5 – Flashit gym"],
    )
    notes: str | None = Field(
        default=None,
        max_length=1000,
        description="Optional climber notes or context (e.g. 'first redpoint attempt').",
    )
    grade_attempted: str | None = Field(
        default=None,
        max_length=20,
        description="The grade the climber believes this route/problem is.",
        examples=["V5", "6c+", "5.12a"],
    )


# ---------------------------------------------------------------------------
# Nested analysis schemas
# ---------------------------------------------------------------------------

class SpecificFeedback(BaseModel):
    """Detailed per-aspect coaching notes from the AI analysis."""

    footwork: str | None = Field(
        default=None, description="Foot placement precision and trust."
    )
    body_positioning: str | None = Field(
        default=None, description="Hip positioning, center of gravity, body rotation."
    )
    arm_usage: str | None = Field(
        default=None, description="Straight-arm vs bent-arm usage, lock-off quality."
    )
    breathing_pacing: str | None = Field(
        default=None, description="Rhythm, rest usage, breathing observations."
    )
    route_reading: str | None = Field(
        default=None, description="Evidence of pre-planning or improvisation."
    )


class FormFeedbackResponse(BaseModel):
    """
    Structured coaching feedback returned after Gemini analysis.
    Maps directly to the JSON structure the Gemini prompt requests.
    """

    model_config = ConfigDict(extra="allow")  # forward-compat with prompt changes

    overall_grade_estimate: str | None = Field(
        default=None,
        description="Estimated difficulty grade of the problem/route.",
        examples=["V4", "6b+"],
    )
    technique_score: int | None = Field(
        default=None, ge=1, le=10, description="Overall technique quality (1–10)."
    )
    body_tension_score: int | None = Field(
        default=None, ge=1, le=10, description="Core and full-body tension quality (1–10)."
    )
    footwork_score: int | None = Field(
        default=None, ge=1, le=10, description="Foot placement and trust (1–10)."
    )
    summary: str | None = Field(
        default=None, description="2–3 sentence overall impression."
    )
    strengths: list[str] = Field(
        default_factory=list, description="Things the climber does well."
    )
    weaknesses: list[str] = Field(
        default_factory=list, description="Areas for improvement."
    )
    specific_feedback: SpecificFeedback | None = Field(
        default=None, description="Detailed per-aspect coaching notes."
    )
    drills_recommended: list[str] = Field(
        default_factory=list, description="Suggested training drills."
    )
    next_steps: str | None = Field(
        default=None, description="Actionable coaching cue for next session."
    )


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class FragmentRequest(BaseModel):
    """Request body for extracting a video fragment."""

    fragment_start: float = Field(..., ge=0, description="Start time in seconds.")
    fragment_end: float = Field(..., gt=0, description="End time in seconds.")


class AnalysisResponse(BaseModel):
    """Response from a video analysis request."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Video ID.")
    status: str | None = Field(default=None, description="Legacy status field.")
    processing_status: str = Field(default="pending", description="Processing status.")
    form_analysis: FormFeedbackResponse | None = Field(
        default=None, description="Coaching feedback."
    )


class VideoUploadResponse(BaseModel):
    """
    Legacy response schema used by v1 upload, fragment, analyze, and list endpoints.
    Maps to the VideoUpload ORM model.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique video ID (UUID).")
    user_id: str = Field(..., description="ID of the user who uploaded.")
    filename: str | None = Field(default=None, description="Original filename.")
    file_path: str | None = Field(default=None, description="Storage path on disk.")
    file_size: int | None = Field(default=None, description="File size in bytes.")
    original_file_path: str | None = Field(default=None, description="Original video path.")
    fragment_file_path: str | None = Field(default=None, description="Fragment video path.")
    status: str | None = Field(default="pending", description="Legacy status.")
    processing_status: str = Field(default="pending", description="Processing status.")
    gemini_file_id: str | None = Field(default=None, description="Gemini File API ID.")
    form_analysis: FormFeedbackResponse | None = Field(
        default=None, description="Coaching feedback."
    )
    form_feedback: str | None = Field(default=None, description="Legacy form feedback text.")
    grade_estimate: str | None = Field(default=None, description="Legacy grade estimate.")
    fragment_start: float | None = Field(default=None, description="Fragment start time.")
    fragment_end: float | None = Field(default=None, description="Fragment end time.")
    notes: str | None = Field(default=None, description="Climber notes.")
    duration: float | None = Field(default=None, description="Video duration in seconds.")
    title: str | None = Field(default=None, description="Human-readable title.")
    grade_attempted: str | None = Field(default=None, description="Climber's estimated grade.")
    created_at: datetime = Field(..., description="Upload timestamp.")
    completed_at: datetime | None = Field(default=None, description="Analysis completion timestamp.")


class VideoResponse(BaseModel):
    """
    Phase 2 response schema for video upload with Gemini File API.
    """

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique video ID (UUID).")
    user_id: str = Field(..., description="ID of the user who uploaded.")
    filename: str = Field(..., description="Original filename.")
    file_size: int = Field(..., description="File size in bytes.")
    file_path: str = Field(..., description="Storage path on disk.")
    gemini_file_id: str | None = Field(
        default=None, description="Gemini File API ID (if uploaded to Gemini)."
    )
    processing_status: str = Field(
        default="pending",
        description="Current processing status: pending, uploading, processing, completed, failed.",
    )
    form_analysis: FormFeedbackResponse | None = Field(
        default=None, description="Coaching feedback (populated when analysis completes)."
    )
    created_at: datetime = Field(..., description="Upload timestamp.")
    completed_at: datetime | None = Field(
        default=None, description="Analysis completion timestamp."
    )
    title: str | None = Field(
        default=None, description="Human-readable title (optional)."
    )
    notes: str | None = Field(
        default=None, description="Climber notes (optional)."
    )
    grade_attempted: str | None = Field(
        default=None, description="Climber's estimated grade."
    )
