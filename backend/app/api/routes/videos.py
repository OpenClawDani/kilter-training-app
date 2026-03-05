"""
FastAPI routes for video upload and climbing form analysis.
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.video import VideoUpload
from app.schemas.video import VideoResponse, FormFeedbackResponse
from app.services.storage_service import save_uploaded_file
from app.services.gemini_service import upload_video_to_gemini, analyze_climbing_form, GeminiAnalysisError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/videos", tags=["videos"])


async def _background_analyze_video(
    video_id: str,
    file_path: str,
    db: Session,
) -> None:
    """
    Background task: upload video to Gemini, analyze, and store results.
    
    This runs asynchronously after the upload endpoint returns.
    Errors are logged but do not affect the HTTP response.
    """
    try:
        # Fetch the video record
        video = db.query(VideoUpload).filter(VideoUpload.id == video_id).first()
        if not video:
            logger.warning("Video %s not found during background analysis", video_id)
            return

        logger.info("Starting background analysis for video %s", video_id)
        video.processing_status = "processing"
        db.commit()

        # Upload to Gemini
        logger.debug("Uploading video %s to Gemini", video_id)
        gemini_file_id = upload_video_to_gemini(file_path)
        video.gemini_file_id = gemini_file_id
        db.commit()

        # Analyze with Gemini
        logger.debug("Analyzing video %s with Gemini", video_id)
        analysis_dict = analyze_climbing_form(gemini_file_id)
        
        # Store analysis results
        video.form_analysis = analysis_dict
        video.processing_status = "completed"
        video.completed_at = datetime.utcnow()
        db.commit()

        logger.info("Analysis completed successfully for video %s", video_id)

    except GeminiAnalysisError as e:
        logger.error("Gemini analysis failed for video %s: %s", video_id, str(e))
        video = db.query(VideoUpload).filter(VideoUpload.id == video_id).first()
        if video:
            video.processing_status = "failed"
            db.commit()
    except Exception as e:
        logger.exception("Unexpected error during background analysis of video %s: %s", video_id, str(e))
        video = db.query(VideoUpload).filter(VideoUpload.id == video_id).first()
        if video:
            video.processing_status = "failed"
            db.commit()


@router.post("/upload", response_model=VideoResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_video(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VideoResponse:
    """
    Upload a climbing video for form analysis.
    
    Returns HTTP 202 Accepted immediately with a video_id.
    The analysis runs asynchronously in the background.
    Poll the GET /{video_id} endpoint to check status and retrieve results.
    
    Args:
        file: Video file (MP4, MOV, AVI, WebM, MPEG)
        background_tasks: FastAPI background task manager
        current_user: Authenticated user
        db: Database session
        
    Returns:
        VideoResponse with initial metadata and processing_status = "uploading"
        
    Raises:
        HTTPException 400: Invalid file type or size exceeds limit
        HTTPException 401: Unauthorized
        HTTPException 500: Unexpected error during upload
    """
    try:
        # Save file locally
        logger.info("Saving uploaded file %s for user %s", file.filename, current_user.id)
        video_id, file_path = await save_uploaded_file(file)

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

        # Queue background analysis
        background_tasks.add_task(
            _background_analyze_video,
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


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> VideoResponse:
    """
    Retrieve a video record by ID, including analysis results if available.
    
    Use this endpoint to poll for completion status and retrieve analysis results.
    
    Args:
        video_id: The video ID returned from the upload endpoint
        current_user: Authenticated user (must own the video)
        db: Database session
        
    Returns:
        VideoResponse with current processing_status and (if complete) form_analysis
        
    Raises:
        HTTPException 404: Video not found or not owned by user
    """
    video = db.query(VideoUpload).filter(
        VideoUpload.id == video_id,
        VideoUpload.user_id == current_user.id,
    ).first()

    if not video:
        logger.warning("Video %s not found for user %s", video_id, current_user.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    # Parse form_analysis if present
    form_analysis = None
    if video.form_analysis:
        try:
            form_analysis = FormFeedbackResponse(**video.form_analysis)
        except Exception as e:
            logger.warning("Failed to parse form_analysis for video %s: %s", video_id, str(e))

    return VideoResponse(
        id=video.id,
        user_id=video.user_id,
        filename=video.filename,
        file_size=video.file_size,
        file_path=video.file_path,
        gemini_file_id=video.gemini_file_id,
        processing_status=video.processing_status,
        form_analysis=form_analysis,
        created_at=video.created_at,
        completed_at=video.completed_at,
    )


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """
    Delete a video and its analysis record (optional cleanup).
    
    Note: Removes only the database record; file cleanup is deferred.
    
    Args:
        video_id: The video ID to delete
        current_user: Authenticated user (must own the video)
        db: Database session
        
    Raises:
        HTTPException 404: Video not found or not owned by user
    """
    video = db.query(VideoUpload).filter(
        VideoUpload.id == video_id,
        VideoUpload.user_id == current_user.id,
    ).first()

    if not video:
        logger.warning("Video %s not found for deletion by user %s", video_id, current_user.id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found")

    logger.info("Deleting video %s", video_id)
    db.delete(video)
    db.commit()
