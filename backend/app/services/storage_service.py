import os
import shutil
import subprocess
import json
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE_MB", "500")) * 1024 * 1024  # bytes
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".webm", ".avi"}


async def save_video(file: UploadFile, user_id: str) -> dict:
    """
    Saves uploaded video to local filesystem.
    Returns: {file_path, file_size, filename}
    """
    # Validate extension
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{ext}' not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Create user upload directory
    user_dir = os.path.join(UPLOAD_DIR, user_id)
    os.makedirs(user_dir, exist_ok=True)

    # Generate unique filename
    import uuid
    filename = f"{uuid.uuid4()}{ext}"
    file_path = os.path.join(user_dir, filename)

    # Save file and track size
    file_size = 0
    with open(file_path, "wb") as f:
        while chunk := await file.read(1024 * 1024):  # 1MB chunks
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                f.close()
                os.remove(file_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                )
            f.write(chunk)

    return {
        "file_path": file_path,
        "file_size": file_size,
        "filename": filename,
    }


async def delete_video(file_path: str) -> bool:
    """Deletes video file from storage."""
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


async def get_file_duration(file_path: str) -> float:
    """Returns video duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                file_path,
            ],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode != 0:
            return 0.0
        info = json.loads(result.stdout)
        return float(info.get("format", {}).get("duration", 0.0))
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return 0.0
