# DAY 3 — CloudCode Kickoff Prompt

> Copy-paste this entire prompt into Claude Code to start Day 3.

---

## CONTEXT

You are implementing Day 3 of Kilter-Up, an AI climbing form analysis app.

**What's already done (Days 1-2):**
- FastAPI backend with auth (JWT), User model, VideoUpload model
- PostgreSQL + Alembic migrations
- Basic project structure

**Day 3 Goal:** Video upload + Gemini Vision form analysis working end-to-end.

**CORE STRATEGY (READ THIS):**
- 🎥 VIDEO = CORE feature. User uploads a climbing video, extracts a fragment, Gemini Vision analyzes their form.
- 📸 PHOTO/circuit detection = supplementary (NOT Day 3 scope).
- Output: "V5 in 45s, body tension good, weak on sloper finish."

---

## DAY 3 TASKS

### TASK 1: Update VideoUpload model for form analysis

Update `backend/app/models/video.py` to reflect form analysis (not circuit detection):

```python
class VideoUpload(Base):
    __tablename__ = "video_uploads"
    
    id: UUID (primary key)
    user_id: UUID (FK → users.id)
    
    # Storage
    original_file_path: str
    fragment_file_path: str (nullable) # trimmed fragment
    
    # Processing
    status: str  # pending / processing / completed / failed
    
    # Gemini Analysis Results
    form_feedback: str (nullable)           # "V5 form solid, weak on sloper finish"
    grade_estimate: str (nullable)          # "V5"
    body_position: JSON (nullable)          # {posture, tension, efficiency_score}
    holds_analysis: JSON (nullable)         # [{position, type, quality}]
    key_weaknesses: JSON (nullable)         # ["weak sloper finish", "low hip position"]
    
    # Fragment settings
    fragment_start: float (nullable)        # seconds
    fragment_end: float (nullable)          # seconds
    
    # Metadata
    notes: str (nullable)                   # user notes
    duration: float (nullable)              # video duration in seconds
    file_size: int (nullable)               # bytes
    
    created_at: DateTime
    updated_at: DateTime
```

Create Alembic migration: `002_update_video_for_form_analysis.py`

---

### TASK 2: Video Pydantic Schemas

Create `backend/app/schemas/video.py`:

```python
class VideoUploadCreate(BaseModel):
    notes: Optional[str] = None

class VideoUploadResponse(BaseModel):
    id: UUID
    status: str
    original_file_path: str
    fragment_file_path: Optional[str]
    form_feedback: Optional[str]
    grade_estimate: Optional[str]
    body_position: Optional[dict]
    holds_analysis: Optional[list]
    key_weaknesses: Optional[list]
    notes: Optional[str]
    duration: Optional[float]
    created_at: datetime

class FragmentRequest(BaseModel):
    video_id: UUID
    fragment_start: float  # seconds
    fragment_end: float    # seconds

class AnalysisResponse(BaseModel):
    form_feedback: str
    grade_estimate: Optional[str]
    body_position: dict
    holds_analysis: list
    key_weaknesses: list
```

---

### TASK 3: Storage Service

Create `backend/app/services/storage_service.py`:

```python
import os, shutil
from fastapi import UploadFile

UPLOAD_DIR = "uploads"  # local dev
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

async def save_video(file: UploadFile, user_id: str) -> dict:
    """
    Saves uploaded video to local filesystem.
    Returns: {file_path, file_size, filename}
    In production, this will upload to S3.
    """
    
async def delete_video(file_path: str) -> bool:
    """Deletes video file from storage."""
    
async def get_file_duration(file_path: str) -> float:
    """Returns video duration in seconds using ffprobe."""
```

---

### TASK 4: Video Fragment Service

Create `backend/app/services/video_service.py`:

```python
import subprocess, os

async def extract_fragment(
    input_path: str,
    output_path: str,
    start: float,
    end: float
) -> str:
    """
    Uses ffmpeg to extract a fragment from a video.
    Returns: output_path of the trimmed fragment.
    
    ffmpeg command:
    ffmpeg -i input.mp4 -ss {start} -to {end} -c copy output.mp4
    """
    
async def get_video_info(file_path: str) -> dict:
    """
    Returns video metadata using ffprobe:
    {duration, width, height, fps, codec}
    """
```

Note: ffmpeg must be installed. Add to requirements or docker.

---

### TASK 5: Gemini Vision Service

Create `backend/app/services/gemini_service.py`:

```python
import google.generativeai as genai
from pathlib import Path

GEMINI_API_KEY = settings.GEMINI_API_KEY  # from env

async def analyze_climbing_form(video_path: str) -> dict:
    """
    Sends video fragment to Gemini Vision for form analysis.
    
    Prompt to Gemini:
    "You are an expert climbing coach analyzing a bouldering video.
    Analyze the climber's form and provide:
    1. Overall form feedback (1-2 sentences)
    2. Grade estimate (e.g. V4, V5)
    3. Body position analysis: posture, tension, efficiency score (0-10)
    4. Holds analysis: for each key hold, position, type, and quality of interaction
    5. Top 3 key weaknesses to improve
    
    Return as JSON with keys: form_feedback, grade_estimate, body_position, holds_analysis, key_weaknesses"
    
    Returns: parsed dict matching AnalysisResponse schema
    """
```

Add `GEMINI_API_KEY` to `.env` and `config.py`.
Add `google-generativeai` to `requirements.txt`.

---

### TASK 6: Video API Router

Create `backend/app/api/videos.py` with these endpoints:

```
POST /api/videos/upload
  auth: required (JWT Bearer)
  form-data: video (file), notes (optional string)
  → saves file, creates VideoUpload record (status=pending)
  → returns VideoUploadResponse with id

POST /api/videos/{video_id}/fragment
  auth: required
  body: FragmentRequest {fragment_start, fragment_end}
  → uses ffmpeg to extract fragment
  → updates VideoUpload record (fragment_file_path)
  → returns VideoUploadResponse

POST /api/videos/{video_id}/analyze
  auth: required
  → calls Gemini Vision on fragment_file_path
  → updates VideoUpload record with analysis results (status=completed)
  → returns AnalysisResponse

GET /api/videos
  auth: required
  → returns list of user's VideoUpload records (latest first)
  → pagination: ?page=1&per_page=10

GET /api/videos/{video_id}
  auth: required
  → returns single VideoUpload with full analysis
```

Register router in `backend/app/main.py`.

---

### TASK 7: Tests

Create `backend/tests/test_videos.py`:

```python
# Test: upload video (mock file)
# Test: fragment extraction (with mock ffmpeg)
# Test: Gemini analysis (mock API call)
# Test: get videos list (pagination)
# Test: get single video
# Test: auth required on all endpoints
# Test: file size validation (>500MB rejected)
# Test: fragment validation (end > start, both > 0)
```

Target: all new tests pass.

---

### TASK 8: Dependencies Update

Add to `backend/requirements.txt`:
```
google-generativeai>=0.8.0
python-multipart>=0.0.9  # for file uploads
aiofiles>=24.0.0
```

Check ffmpeg is available (add to docker-compose or note in README).

---

## ACCEPTANCE CRITERIA (Day 3 Done When...)

- [ ] POST /api/videos/upload accepts MP4/MOV/WebM (max 500MB), returns video_id
- [ ] POST /api/videos/{id}/fragment extracts clip with ffmpeg
- [ ] POST /api/videos/{id}/analyze calls Gemini, returns form_feedback + analysis
- [ ] GET /api/videos returns paginated list
- [ ] All new tests pass (`pytest backend/tests/test_videos.py -v`)
- [ ] No secrets in code (GEMINI_API_KEY in .env only)
- [ ] Migration 002 applied cleanly
- [ ] Commit + push to main

---

## ENVIRONMENT VARIABLES

Add to `.env`:
```
GEMINI_API_KEY=your_key_here
UPLOAD_DIR=uploads
MAX_FILE_SIZE_MB=500
```

---

## HOW TO GET GEMINI API KEY

1. Go to: https://aistudio.google.com/apikey
2. Create API key (free tier: 15 requests/min, sufficient for dev)
3. Add to `.env` as GEMINI_API_KEY

---

## COMMIT SEQUENCE

```
feat: update VideoUpload model for form analysis + migration 002
feat: add storage service (local file handling)
feat: add video fragment service (ffmpeg)
feat: add Gemini Vision service (form analysis)
feat: add video upload + analyze API endpoints
test: add video endpoint tests
docs: update README with Day 3 progress
```

---

## START HERE

Read CLAUDE.md first, then implement tasks in order 1→8.
Ask if anything is unclear before starting. Don't change auth system.
Good luck! 🧗
