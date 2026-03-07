from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query, BackgroundTasks, status
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Optional
import os
import logging
from datetime import datetime

from app.core.database import get_db, SessionLocal
from app.core.deps import get_current_user
from app.models.user import User
from app.models.video import VideoUpload
from app.schemas.video import (
    VideoUploadResponse,
    FragmentRequest,
    AnalysisResponse,
    VideoResponse,
    FormFeedbackResponse,
)
from app.services import storage_service, video_service, gemini_service
from app.services.gemini_service import upload_video_to_gemini, analyze_climbing_form

logger = logging.getLogger(__name__)
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


async def _run_analysis(video_id: str, analysis_path: str):
    """Background task: runs Gemini analysis and updates DB record (legacy)."""
    db = SessionLocal()
    try:
        video_record = db.execute(
            select(VideoUpload).where(VideoUpload.id == video_id)
        ).scalars().first()
        if not video_record:
            return

        result = await gemini_service.analyze_climbing_form(analysis_path)

        video_record.form_feedback = result["form_feedback"]
        video_record.grade_estimate = result.get("grade_estimate")
        video_record.body_position = result.get("body_position")
        video_record.holds_analysis = result.get("holds_analysis")
        video_record.key_weaknesses = result.get("key_weaknesses")
        video_record.status = "completed"
        db.commit()
    except Exception:
        video_record = db.execute(
            select(VideoUpload).where(VideoUpload.id == video_id)
        ).scalars().first()
        if video_record:
            video_record.status = "failed"
            db.commit()
    finally:
        db.close()


async def _background_analyze_phase2(
    video_id: str,
    file_path: str,
    db: Session,
) -> None:
    """Background task: upload to Gemini File API and analyze (Phase 2)."""
    try:
        video = db.query(VideoUpload).filter(VideoUpload.id == video_id).first()
        if not video:
            logger.warning("Video %s not found during background analysis", video_id)
            return

        logger.info("Starting Phase 2 background analysis for video %s", video_id)
        video.processing_status = "processing"
        db.commit()

        # Upload to Gemini File API
        logger.debug("Uploading video %s to Gemini", video_id)
        gemini_file_id = upload_video_to_gemini(file_path)
        video.gemini_file_id = gemini_file_id
        db.commit()

        # Analyze with Gemini
        logger.debug("Analyzing video %s with Gemini", video_id)
        analysis_dict = analyze_climbing_form(gemini_file_id)
        
        # Store results
        video.form_analysis = analysis_dict
        video.processing_status = "completed"
        video.completed_at = datetime.utcnow()
        db.commit()

        logger.info("Phase 2 analysis completed for video %s", video_id)

    except Exception as e:
        logger.error("Phase 2 analysis failed for video %s: %s", video_id, str(e))
        video = db.query(VideoUpload).filter(VideoUpload.id == video_id).first()
        if video:
            video.processing_status = "failed"
            db.commit()
    finally:
        db.close()


@router.post("/{video_id}/analyze", response_model=VideoUploadResponse, status_code=202)
async def analyze_video(
    video_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Start Gemini Vision analysis on a video (or its fragment).
    Returns 202 Accepted immediately — poll GET /api/videos/{id} for results.
    """
    video_record = db.execute(
        select(VideoUpload).where(
            VideoUpload.id == video_id,
            VideoUpload.user_id == current_user.id,
        )
    ).scalars().first()

    if not video_record:
        raise HTTPException(status_code=404, detail="Video not found")

    analysis_path = video_record.fragment_file_path or video_record.original_file_path

    video_record.status = "processing"
    db.commit()
    db.refresh(video_record)

    background_tasks.add_task(_run_analysis, video_id, analysis_path)

    return VideoUploadResponse.model_validate(video_record)


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


@router.post("/v2/upload", response_model=VideoResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_video_phase2(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VideoResponse:
    """
    [PHASE 2] Upload a climbing video for form analysis.
    Uses Gemini File API for direct video processing.
    
    Returns HTTP 202 Accepted with video_id.
    Poll GET /api/videos/{video_id} to check status and retrieve results.
    """
    try:
        # Save file locally
        logger.info("Saving uploaded file %s for user %s", file.filename, current_user.id)
        video_id, file_path = await storage_service.save_video(file, str(current_user.id))

        # Create database record
        video_upload = VideoUpload(
            id=video_id,
            user_id=current_user.id,
            filename=file.filename or "upload",
            file_size=file.size or 0,
            file_path=file_path,
            processing_status="uploading",
        )
        db.add(video_upload)
        db.commit()
        db.refresh(video_upload)

        logger.info("Video %s created in database, queuing background analysis", video_id)

        # Queue background analysis (Phase 2 Gemini File API)
        background_tasks.add_task(
            _background_analyze_phase2,
            video_id,
            file_path,
            db,
        )

        return VideoResponse(
            id=video_upload.id,
            user_id=video_upload.user_id,
            filename=video_upload.filename,
            file_size=video_upload.file_size,
            file_path=video_upload.file_path,
            gemini_file_id=video_upload.gemini_file_id,
            processing_status=video_upload.processing_status,
            created_at=video_upload.created_at,
        )

    except ValueError as e:
        logger.warning("File validation failed: %s", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except IOError as e:
        logger.error("File storage failed: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    except Exception as e:
        logger.exception("Unexpected error during upload: %s", str(e))
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Upload failed")


@router.get("/{video_id}", response_model=VideoUploadResponse)
async def get_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a single video with full analysis results (legacy + Phase 2)."""
    video_record = db.execute(
        select(VideoUpload).where(
            VideoUpload.id == video_id,
            VideoUpload.user_id == current_user.id,
        )
    ).scalars().first()

    if not video_record:
        raise HTTPException(status_code=404, detail="Video not found")

    return VideoUploadResponse.model_validate(video_record)
