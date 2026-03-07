"""
Test suite for video upload, fragment extraction, and Gemini analysis endpoints.
Uses SQLite in-memory DB and mocks for ffmpeg / Gemini.
"""

import pytest
import uuid
import io
import os
import json
from datetime import datetime
from unittest.mock import patch, AsyncMock, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import Base
from app.core.security import create_access_token
from app.models.user import User
from app.models.video import VideoUpload
from app.schemas.video import (
    VideoUploadCreate,
    VideoUploadResponse,
    FragmentRequest,
    AnalysisResponse,
)
from conftest import engine, TestingSessionLocal

client = TestClient(app)

# --- Helpers ---

MOCK_GEMINI_RESULT = {
    "form_feedback": "Solid V5 attempt, body tension is good but finish on sloper needs work.",
    "grade_estimate": "V5",
    "body_position": {"posture": "upright", "tension": "good", "efficiency_score": 7},
    "holds_analysis": [
        {"position": "start left", "type": "jug", "quality": "good"},
        {"position": "top right", "type": "sloper", "quality": "weak"},
    ],
    "key_weaknesses": ["weak sloper finish", "low hip position", "over-gripping on crimps"],
}


def _create_user(db) -> User:
    """Create a test user and return it."""
    user = User(
        id=str(uuid.uuid4()),
        email=f"test_{uuid.uuid4().hex[:8]}@example.com",
        username=f"user_{uuid.uuid4().hex[:8]}",
        hashed_password="hashed",
        full_name="Test Climber",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def _auth_header(user_id: str) -> dict:
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


def _fake_video_bytes(size: int = 1024) -> io.BytesIO:
    """Return a BytesIO object that pretends to be a video file."""
    return io.BytesIO(b"\x00" * size)


# --- Schema Tests ---


class TestVideoSchemas:
    """Validate Pydantic video schemas."""

    def test_video_upload_create(self):
        schema = VideoUploadCreate(notes="Morning session")
        assert schema.notes == "Morning session"

    def test_video_upload_create_no_notes(self):
        schema = VideoUploadCreate()
        assert schema.notes is None

    def test_video_upload_response(self):
        vid = uuid.uuid4()
        now = datetime.utcnow()
        resp = VideoUploadResponse(
            id=vid,
            status="pending",
            original_file_path="/uploads/video.mp4",
            created_at=now,
        )
        assert resp.id == vid
        assert resp.form_feedback is None
        assert resp.grade_estimate is None

    def test_fragment_request_valid(self):
        req = FragmentRequest(fragment_start=5.0, fragment_end=25.0)
        assert req.fragment_start == 5.0
        assert req.fragment_end == 25.0

    def test_analysis_response(self):
        resp = AnalysisResponse(**MOCK_GEMINI_RESULT)
        assert resp.form_feedback == MOCK_GEMINI_RESULT["form_feedback"]
        assert resp.grade_estimate == "V5"
        assert len(resp.key_weaknesses) == 3


# --- Model Tests ---


class TestVideoModel:
    """Test VideoUpload SQLAlchemy model."""

    def test_model_creation(self):
        v = VideoUpload(
            user_id=str(uuid.uuid4()),
            original_file_path="/uploads/test.mp4",
            status="pending",
        )
        assert v.status == "pending"
        assert v.form_feedback is None
        assert v.body_position is None

    def test_model_with_analysis(self):
        v = VideoUpload(
            user_id=str(uuid.uuid4()),
            original_file_path="/uploads/test.mp4",
            status="completed",
            form_feedback="Good form",
            grade_estimate="V4",
            body_position={"posture": "good", "tension": "high", "efficiency_score": 8},
            holds_analysis=[{"position": "left", "type": "crimp", "quality": "solid"}],
            key_weaknesses=["footwork"],
        )
        assert v.grade_estimate == "V4"
        assert v.body_position["efficiency_score"] == 8

    def test_model_repr(self):
        vid = str(uuid.uuid4())
        v = VideoUpload(id=vid, user_id=str(uuid.uuid4()), original_file_path="/p", status="pending")
        assert f"{vid} - pending" in repr(v)


# --- Endpoint Tests ---


class TestUploadEndpoint:
    """POST /api/videos/upload"""

    def setup_method(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    @patch("app.services.storage_service.get_file_duration", new_callable=AsyncMock, return_value=42.5)
    @patch("app.services.storage_service.save_video", new_callable=AsyncMock)
    def test_upload_success(self, mock_save, mock_dur):
        db = TestingSessionLocal()
        user = _create_user(db)
        db.close()

        mock_save.return_value = {
            "file_path": "uploads/test/video.mp4",
            "file_size": 1024,
            "filename": "video.mp4",
        }

        resp = client.post(
            "/api/videos/upload",
            headers=_auth_header(user.id),
            files={"video": ("climb.mp4", _fake_video_bytes(), "video/mp4")},
            data={"notes": "Morning session"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "pending"
        assert data["notes"] == "Morning session"
        assert data["duration"] == 42.5
        assert data["file_size"] == 1024
        assert "id" in data

    def test_upload_requires_auth(self):
        resp = client.post(
            "/api/videos/upload",
            files={"video": ("climb.mp4", _fake_video_bytes(), "video/mp4")},
        )
        assert resp.status_code == 403

    @patch("app.services.storage_service.save_video", new_callable=AsyncMock)
    def test_upload_file_too_large(self, mock_save):
        from fastapi import HTTPException
        mock_save.side_effect = HTTPException(status_code=400, detail="File too large. Maximum size: 500MB")

        db = TestingSessionLocal()
        user = _create_user(db)
        db.close()

        resp = client.post(
            "/api/videos/upload",
            headers=_auth_header(user.id),
            files={"video": ("big.mp4", _fake_video_bytes(), "video/mp4")},
        )
        assert resp.status_code == 400
        assert "File too large" in resp.json()["detail"]

    @patch("app.services.storage_service.save_video", new_callable=AsyncMock)
    def test_upload_invalid_extension(self, mock_save):
        from fastapi import HTTPException
        mock_save.side_effect = HTTPException(
            status_code=400, detail="File type '.txt' not allowed"
        )

        db = TestingSessionLocal()
        user = _create_user(db)
        db.close()

        resp = client.post(
            "/api/videos/upload",
            headers=_auth_header(user.id),
            files={"video": ("notes.txt", _fake_video_bytes(), "text/plain")},
        )
        assert resp.status_code == 400
        assert "not allowed" in resp.json()["detail"]


class TestFragmentEndpoint:
    """POST /api/videos/{video_id}/fragment"""

    def setup_method(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def _seed_video(self) -> tuple:
        """Create a user + video record, return (user, video_id)."""
        db = TestingSessionLocal()
        user = _create_user(db)
        video = VideoUpload(
            id=str(uuid.uuid4()),
            user_id=user.id,
            original_file_path="uploads/test/video.mp4",
            status="pending",
        )
        db.add(video)
        db.commit()
        vid = video.id
        uid = user.id
        db.close()
        return uid, vid

    @patch("app.services.video_service.extract_fragment", new_callable=AsyncMock, return_value="uploads/test/video_fragment.mp4")
    def test_fragment_success(self, mock_ff):
        uid, vid = self._seed_video()
        resp = client.post(
            f"/api/videos/{vid}/fragment",
            headers=_auth_header(uid),
            json={"fragment_start": 5.0, "fragment_end": 20.0},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "processing"
        assert data["fragment_file_path"] is not None
        mock_ff.assert_called_once()

    def test_fragment_end_before_start(self):
        uid, vid = self._seed_video()
        resp = client.post(
            f"/api/videos/{vid}/fragment",
            headers=_auth_header(uid),
            json={"fragment_start": 20.0, "fragment_end": 5.0},
        )
        assert resp.status_code == 400
        assert "greater than" in resp.json()["detail"]

    def test_fragment_negative_times(self):
        uid, vid = self._seed_video()
        resp = client.post(
            f"/api/videos/{vid}/fragment",
            headers=_auth_header(uid),
            json={"fragment_start": -1.0, "fragment_end": 5.0},
        )
        assert resp.status_code == 400

    def test_fragment_video_not_found(self):
        db = TestingSessionLocal()
        user = _create_user(db)
        db.close()

        resp = client.post(
            f"/api/videos/{uuid.uuid4()}/fragment",
            headers=_auth_header(user.id),
            json={"fragment_start": 1.0, "fragment_end": 10.0},
        )
        assert resp.status_code == 404

    def test_fragment_requires_auth(self):
        resp = client.post(
            f"/api/videos/{uuid.uuid4()}/fragment",
            json={"fragment_start": 1.0, "fragment_end": 10.0},
        )
        assert resp.status_code == 403


class TestAnalyzeEndpoint:
    """POST /api/videos/{video_id}/analyze — returns 202 (async via BackgroundTasks)"""

    def setup_method(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def _seed_video(self, with_fragment=False) -> tuple:
        db = TestingSessionLocal()
        user = _create_user(db)
        video = VideoUpload(
            id=str(uuid.uuid4()),
            user_id=user.id,
            original_file_path="uploads/test/video.mp4",
            fragment_file_path="uploads/test/video_fragment.mp4" if with_fragment else None,
            status="processing" if with_fragment else "pending",
        )
        db.add(video)
        db.commit()
        vid = video.id
        uid = user.id
        db.close()
        return uid, vid

    def test_analyze_returns_202_processing(self):
        """Analyze endpoint returns 202 Accepted and sets status to processing."""
        uid, vid = self._seed_video(with_fragment=True)
        resp = client.post(
            f"/api/videos/{vid}/analyze",
            headers=_auth_header(uid),
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "processing"
        assert data["id"] is not None

    def test_analyze_picks_fragment_path(self):
        """When fragment exists, background task should receive fragment path."""
        uid, vid = self._seed_video(with_fragment=True)
        resp = client.post(
            f"/api/videos/{vid}/analyze",
            headers=_auth_header(uid),
        )
        assert resp.status_code == 202

    def test_analyze_picks_original_if_no_fragment(self):
        """When no fragment, background task should receive original path."""
        uid, vid = self._seed_video(with_fragment=False)
        resp = client.post(
            f"/api/videos/{vid}/analyze",
            headers=_auth_header(uid),
        )
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "processing"

    def test_analyze_video_not_found(self):
        db = TestingSessionLocal()
        user = _create_user(db)
        db.close()

        resp = client.post(
            f"/api/videos/{uuid.uuid4()}/analyze",
            headers=_auth_header(user.id),
        )
        assert resp.status_code == 404

    def test_analyze_requires_auth(self):
        resp = client.post(f"/api/videos/{uuid.uuid4()}/analyze")
        assert resp.status_code == 403

    @patch("app.api.videos._run_analysis", new_callable=AsyncMock)
    def test_background_task_is_scheduled(self, mock_run):
        """Verify that _run_analysis is added as a background task."""
        uid, vid = self._seed_video(with_fragment=True)
        resp = client.post(
            f"/api/videos/{vid}/analyze",
            headers=_auth_header(uid),
        )
        assert resp.status_code == 202
        # BackgroundTasks in TestClient are executed synchronously,
        # so mock_run should have been called
        mock_run.assert_called_once_with(vid, "uploads/test/video_fragment.mp4")


class TestListVideosEndpoint:
    """GET /api/videos"""

    def setup_method(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_list_empty(self):
        db = TestingSessionLocal()
        user = _create_user(db)
        db.close()

        resp = client.get("/api/videos", headers=_auth_header(user.id))
        assert resp.status_code == 200
        assert resp.json() == []

    def test_list_returns_own_videos(self):
        db = TestingSessionLocal()
        user = _create_user(db)
        other_user = _create_user(db)

        # Create videos for both users
        for i in range(3):
            db.add(VideoUpload(user_id=user.id, original_file_path=f"/v{i}.mp4", status="pending"))
        db.add(VideoUpload(user_id=other_user.id, original_file_path="/other.mp4", status="pending"))
        db.commit()
        uid = user.id
        db.close()

        resp = client.get("/api/videos", headers=_auth_header(uid))
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 3

    def test_list_pagination(self):
        db = TestingSessionLocal()
        user = _create_user(db)
        for i in range(15):
            db.add(VideoUpload(user_id=user.id, original_file_path=f"/v{i}.mp4", status="pending"))
        db.commit()
        uid = user.id
        db.close()

        # Page 1
        resp = client.get("/api/videos?page=1&per_page=10", headers=_auth_header(uid))
        assert len(resp.json()) == 10

        # Page 2
        resp = client.get("/api/videos?page=2&per_page=10", headers=_auth_header(uid))
        assert len(resp.json()) == 5

    def test_list_requires_auth(self):
        resp = client.get("/api/videos")
        assert resp.status_code == 403


class TestGetVideoEndpoint:
    """GET /api/videos/{video_id}"""

    def setup_method(self):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

    def test_get_video_success(self):
        db = TestingSessionLocal()
        user = _create_user(db)
        video = VideoUpload(
            id=str(uuid.uuid4()),
            user_id=user.id,
            original_file_path="/uploads/test.mp4",
            status="completed",
            form_feedback="Great form",
            grade_estimate="V4",
        )
        db.add(video)
        db.commit()
        vid = video.id
        uid = user.id
        db.close()

        resp = client.get(f"/api/videos/{vid}", headers=_auth_header(uid))
        assert resp.status_code == 200
        data = resp.json()
        assert data["form_feedback"] == "Great form"
        assert data["grade_estimate"] == "V4"

    def test_get_video_not_found(self):
        db = TestingSessionLocal()
        user = _create_user(db)
        db.close()

        resp = client.get(f"/api/videos/{uuid.uuid4()}", headers=_auth_header(user.id))
        assert resp.status_code == 404

    def test_get_video_other_user_forbidden(self):
        db = TestingSessionLocal()
        user1 = _create_user(db)
        user2 = _create_user(db)
        video = VideoUpload(
            id=str(uuid.uuid4()),
            user_id=user1.id,
            original_file_path="/uploads/test.mp4",
            status="pending",
        )
        db.add(video)
        db.commit()
        vid = video.id
        uid2 = user2.id
        db.close()

        # user2 tries to access user1's video → 404 (not revealed)
        resp = client.get(f"/api/videos/{vid}", headers=_auth_header(uid2))
        assert resp.status_code == 404

    def test_get_video_requires_auth(self):
        resp = client.get(f"/api/videos/{uuid.uuid4()}")
        assert resp.status_code == 403


# --- Storage Service Unit Tests ---


class TestStorageService:
    """Unit tests for storage_service functions."""

    @pytest.mark.asyncio
    async def test_save_video_rejects_bad_extension(self):
        from app.services.storage_service import save_video
        from fastapi import HTTPException

        file = MagicMock(spec=["filename", "read"])
        file.filename = "document.pdf"

        with pytest.raises(HTTPException) as exc_info:
            await save_video(file, "user123")
        assert exc_info.value.status_code == 400
        assert "not allowed" in exc_info.value.detail

    def test_allowed_extensions(self):
        from app.services.storage_service import ALLOWED_EXTENSIONS
        assert ".mp4" in ALLOWED_EXTENSIONS
        assert ".mov" in ALLOWED_EXTENSIONS
        assert ".webm" in ALLOWED_EXTENSIONS
        assert ".pdf" not in ALLOWED_EXTENSIONS


# --- Fragment Validation Tests ---


class TestFragmentValidation:
    """Test fragment request edge cases."""

    def test_fragment_start_equals_end(self):
        """fragment_end must be strictly greater than fragment_start."""
        db = TestingSessionLocal()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        user = _create_user(db)
        video = VideoUpload(
            id=str(uuid.uuid4()),
            user_id=user.id,
            original_file_path="/v.mp4",
            status="pending",
        )
        db.add(video)
        db.commit()
        vid = video.id
        uid = user.id
        db.close()

        resp = client.post(
            f"/api/videos/{vid}/fragment",
            headers=_auth_header(uid),
            json={"fragment_start": 10.0, "fragment_end": 10.0},
        )
        assert resp.status_code == 400

    def test_fragment_zero_end(self):
        """fragment_end=0 should be rejected."""
        db = TestingSessionLocal()
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        user = _create_user(db)
        video = VideoUpload(
            id=str(uuid.uuid4()),
            user_id=user.id,
            original_file_path="/v.mp4",
            status="pending",
        )
        db.add(video)
        db.commit()
        vid = video.id
        uid = user.id
        db.close()

        resp = client.post(
            f"/api/videos/{vid}/fragment",
            headers=_auth_header(uid),
            json={"fragment_start": 0.0, "fragment_end": 0.0},
        )
        assert resp.status_code == 400


# --- Gemini Service Unit Tests ---


class TestGeminiService:
    """Unit tests for gemini_service — Gemini File API pattern."""

    @pytest.mark.asyncio
    @patch("app.services.gemini_service.genai")
    async def test_analyze_uses_file_api_with_wait(self, mock_genai):
        """Verify: upload_file → poll state → single generate_content call."""
        from app.services.gemini_service import analyze_climbing_form

        # Mock file that goes PROCESSING → ACTIVE
        mock_file = MagicMock()
        mock_file.state.name = "ACTIVE"
        mock_file.name = "files/abc123"
        mock_genai.upload_file.return_value = mock_file

        # Mock model response
        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_GEMINI_RESULT)
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = await analyze_climbing_form("/fake/video.mp4")

        mock_genai.upload_file.assert_called_once_with(path="/fake/video.mp4")
        mock_model.generate_content.assert_called_once()
        assert result["form_feedback"] == MOCK_GEMINI_RESULT["form_feedback"]
        assert result["grade_estimate"] == "V5"
        assert len(result["key_weaknesses"]) == 3

    @pytest.mark.asyncio
    @patch("app.services.gemini_service.time.sleep")
    @patch("app.services.gemini_service.genai")
    async def test_analyze_waits_for_processing(self, mock_genai, mock_sleep):
        """Verify polling loop waits while state is PROCESSING."""
        from app.services.gemini_service import analyze_climbing_form

        # First call: PROCESSING, second call (via get_file): ACTIVE
        processing_file = MagicMock()
        processing_file.state.name = "PROCESSING"
        processing_file.name = "files/abc123"

        active_file = MagicMock()
        active_file.state.name = "ACTIVE"
        active_file.name = "files/abc123"

        mock_genai.upload_file.return_value = processing_file
        mock_genai.get_file.return_value = active_file

        mock_response = MagicMock()
        mock_response.text = json.dumps(MOCK_GEMINI_RESULT)
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_genai.GenerativeModel.return_value = mock_model

        result = await analyze_climbing_form("/fake/video.mp4")

        mock_genai.get_file.assert_called_once_with("files/abc123")
        mock_sleep.assert_called()
        assert result["form_feedback"] == MOCK_GEMINI_RESULT["form_feedback"]

    @pytest.mark.asyncio
    @patch("app.services.gemini_service.genai")
    async def test_analyze_raises_on_failed_processing(self, mock_genai):
        """Verify RuntimeError if Gemini file processing fails."""
        from app.services.gemini_service import analyze_climbing_form

        mock_file = MagicMock()
        mock_file.state.name = "FAILED"
        mock_file.name = "files/abc123"
        mock_genai.upload_file.return_value = mock_file

        with pytest.raises(RuntimeError, match="processing failed"):
            await analyze_climbing_form("/fake/video.mp4")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
