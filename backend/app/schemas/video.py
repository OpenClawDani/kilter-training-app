"""
Pydantic v2 schemas for video upload and analysis responses.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, ConfigDict


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
        default=None, ge=1, le=10, description="Overall technique quality (1-10)."
    )
    body_tension_score: int | None = Field(
        default=None, ge=1, le=10, description="Core and full-body tension quality (1-10)."
    )
    footwork_score: int | None = Field(
        default=None, ge=1, le=10, description="Foot placement and trust (1-10)."
    )
    summary: str | None = Field(
        default=None, description="2-3 sentence overall impression."
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

class VideoResponse(BaseModel):
    """Response schema for video endpoints."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique video ID (UUID).")
    user_id: str = Field(..., description="ID of the user who uploaded.")
    filename: str | None = Field(default=None, description="Original filename.")
    file_size: int | None = Field(default=None, description="File size in bytes.")
    processing_status: str = Field(
        default="pending",
        description="Current processing status: pending, processing, completed, failed.",
    )
    form_analysis: FormFeedbackResponse | None = Field(
        default=None, description="Coaching feedback (populated when analysis completes)."
    )
    created_at: datetime = Field(..., description="Upload timestamp.")
    completed_at: datetime | None = Field(
        default=None, description="Analysis completion timestamp."
    )
    title: str | None = Field(default=None, description="Human-readable title.")
    grade_attempted: str | None = Field(
        default=None, description="Climber's estimated grade."
    )
