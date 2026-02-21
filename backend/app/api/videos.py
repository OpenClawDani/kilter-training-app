from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import os

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.video import VideoUpload
from app.schemas.video import (
    VideoUploadResponse,
    FragmentRequest,
    AnalysisResponse,
)
from app.services import storage_service, video_service, gemini_service

router = APIRouter()


@router.post("/upload", response_model=VideoUploadResponse, status_code=201)
async def upload_video(
    video: UploadFile = File(...),
    notes: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload a climbing video for analysis."""
    file_info = await storage_service.save_video(video, str(current_user.id))

    duration = await storage_service.get_file_duration(file_info["file_path"])

    video_record = VideoUpload(
        user_id=current_user.id,
        original_file_path=file_info["file_path"],
        file_size=file_info["file_size"],
        duration=duration,
        notes=notes,
        status="pending",
    )
    db.add(video_record)
    db.commit()
    db.refresh(video_record)

    return VideoUploadResponse.model_validate(video_record)


@router.post("/{video_id}/fragment", response_model=VideoUploadResponse)
async def create_fragment(
    video_id: str,
    request: FragmentRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Extract a fragment from an uploaded video using ffmpeg."""
    video_record = db.execute(
        select(VideoUpload).where(
            VideoUpload.id == video_id,
            VideoUpload.user_id == current_user.id,
        )
    ).scalars().first()

    if not video_record:
        raise HTTPException(status_code=404, detail="Video not found")

    if request.fragment_start < 0 or request.fragment_end <= 0:
        raise HTTPException(status_code=400, detail="Fragment times must be positive")
    if request.fragment_end <= request.fragment_start:
        raise HTTPException(status_code=400, detail="fragment_end must be greater than fragment_start")

    base, ext = os.path.splitext(video_record.original_file_path)
    fragment_path = f"{base}_fragment{ext}"

    await video_service.extract_fragment(
        input_path=video_record.original_file_path,
        output_path=fragment_path,
        start=request.fragment_start,
        end=request.fragment_end,
    )

    video_record.fragment_file_path = fragment_path
    video_record.fragment_start = request.fragment_start
    video_record.fragment_end = request.fragment_end
    video_record.status = "processing"
    db.commit()
    db.refresh(video_record)

    return VideoUploadResponse.model_validate(video_record)


@router.post("/{video_id}/analyze", response_model=AnalysisResponse)
async def analyze_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Run Gemini Vision analysis on a video (or its fragment)."""
    video_record = db.execute(
        select(VideoUpload).where(
            VideoUpload.id == video_id,
            VideoUpload.user_id == current_user.id,
        )
    ).scalars().first()

    if not video_record:
        raise HTTPException(status_code=404, detail="Video not found")

    analysis_path = video_record.fragment_file_path or video_record.original_file_path

    try:
        result = await gemini_service.analyze_climbing_form(analysis_path)
    except Exception as e:
        video_record.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    video_record.form_feedback = result["form_feedback"]
    video_record.grade_estimate = result.get("grade_estimate")
    video_record.body_position = result.get("body_position")
    video_record.holds_analysis = result.get("holds_analysis")
    video_record.key_weaknesses = result.get("key_weaknesses")
    video_record.status = "completed"
    db.commit()
    db.refresh(video_record)

    return AnalysisResponse(**result)


@router.get("", response_model=list[VideoUploadResponse])
async def list_videos(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get paginated list of current user's videos (latest first)."""
    offset = (page - 1) * per_page
    videos = db.execute(
        select(VideoUpload)
        .where(VideoUpload.user_id == current_user.id)
        .order_by(VideoUpload.created_at.desc())
        .offset(offset)
        .limit(per_page)
    ).scalars().all()

    return [VideoUploadResponse.model_validate(v) for v in videos]


@router.get("/{video_id}", response_model=VideoUploadResponse)
async def get_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single video with full analysis results."""
    video_record = db.execute(
        select(VideoUpload).where(
            VideoUpload.id == video_id,
            VideoUpload.user_id == current_user.id,
        )
    ).scalars().first()

    if not video_record:
        raise HTTPException(status_code=404, detail="Video not found")

    return VideoUploadResponse.model_validate(video_record)
