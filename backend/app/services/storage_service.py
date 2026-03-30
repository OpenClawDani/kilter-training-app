"""
Local file storage service for uploaded climbing videos.
"""

import os
import uuid
import logging
from pathlib import Path

from fastapi import UploadFile

logger = logging.getLogger(__name__)

# Resolve uploads directory from UPLOAD_DIR env var (same as Railway config).
# Falls back to <project_root>/uploads for local dev.
_DEFAULT_UPLOADS_DIR = Path(__file__).resolve().parents[3] / "uploads"
UPLOADS_DIR = Path(os.getenv("UPLOAD_DIR", str(_DEFAULT_UPLOADS_DIR)))

ALLOWED_MIME_TYPES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/webm",
    "video/mpeg",
}

MAX_FILE_SIZE_BYTES = 500 * 1024 * 1024  # 500 MB


def _ensure_uploads_dir() -> None:
    """Create the uploads directory if it does not exist."""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    logger.debug("Uploads directory ensured: %s", UPLOADS_DIR)


def save_uploaded_file(file: UploadFile) -> tuple[str, str]:
    """
    Persist an uploaded video file to local storage.

    Args:
        file: The FastAPI UploadFile object from the request.

    Returns:
        A tuple of (video_id, file_path) where:
          - video_id is a unique string identifier (UUID4)
          - file_path is the absolute path to the saved file on disk

    Raises:
        ValueError: If the MIME type is not allowed or the file exceeds the size limit.
        IOError: If writing to disk fails.
    """
    _ensure_uploads_dir()

    # Validate MIME type
    content_type = file.content_type or ""
    if content_type not in ALLOWED_MIME_TYPES:
        raise ValueError(
            f"Unsupported file type '{content_type}'. "
            f"Allowed types: {', '.join(sorted(ALLOWED_MIME_TYPES))}"
        )

    # Derive a safe file extension
    original_name = file.filename or "upload"
    suffix = Path(original_name).suffix.lower() or ".mp4"

    video_id = str(uuid.uuid4())
    dest_filename = f"{video_id}{suffix}"
    dest_path = UPLOADS_DIR / dest_filename

    logger.info(
        "Saving uploaded file '%s' → '%s'", original_name, dest_path
    )

    try:
        total_bytes = 0
        chunk_size = 1024 * 1024  # 1 MB chunks

        with open(dest_path, "wb") as out_file:
            while True:
                chunk = file.file.read(chunk_size)
                if not chunk:
                    break
                total_bytes += len(chunk)
                if total_bytes > MAX_FILE_SIZE_BYTES:
                    out_file.close()
                    dest_path.unlink(missing_ok=True)
                    raise ValueError(
                        f"File exceeds maximum allowed size of "
                        f"{MAX_FILE_SIZE_BYTES // (1024 * 1024)} MB."
                    )
                out_file.write(chunk)

    except ValueError:
        raise
    except Exception as exc:
        # Clean up partial file on any write error
        dest_path.unlink(missing_ok=True)
        raise IOError(f"Failed to save uploaded file: {exc}") from exc

    logger.info(
        "File saved successfully: %s (%.2f MB)",
        dest_path,
        total_bytes / (1024 * 1024),
    )
    return video_id, str(dest_path)
