# 🚀 CloudCode Planning Guide - Kilter Up

**Purpose:** Detailed sprint breakdown for CloudCode AI development  
**Scope:** Week 1 (Feb 18-22, 2026)  
**Status:** Ready for CloudCode discussion

---

## 📋 Week 1 Sprint - Core Foundation

### Monday (Feb 18) - Database & Auth Setup

#### Task 1.1: Database Schema & SQLAlchemy Models
**Deliverable:** `backend/models/`  
**Files to create:**
- `backend/models/__init__.py`
- `backend/models/user.py` - User model + password hashing
- `backend/models/circuit.py` - Circuit model (all types)
- `backend/models/video.py` - VideoUpload model
- `backend/models/training_log.py` - TrainingLog model

**Acceptance Criteria:**
- ✅ All SQLAlchemy models match DATABASE_SCHEMA.sql
- ✅ Relationships defined correctly (Foreign Keys)
- ✅ Type hints on all fields
- ✅ Docstrings on each model class
- ✅ Models can be imported without errors

**Prompt for CloudCode:**
```
Crea i modelli SQLAlchemy per Kilter Up basandoti su DATABASE_SCHEMA.sql.
File: backend/models/

Requisiti:
1. User model con password hashing (bcrypt)
2. Circuit model con JSONB support per holds
3. VideoUpload model con status tracking
4. TrainingLog model
5. All models inherit from Base
6. Use proper typing annotations
7. Add docstrings

Usa PostgreSQL dialect per JSONB fields.
Non aggiungere logica di business, solo ORM definitions.
```

---

#### Task 1.2: Authentication Endpoints
**Deliverable:** `backend/routes/auth.py`  
**Endpoints:**
- POST `/auth/register` - Create user
- POST `/auth/login` - Login + JWT token
- GET `/auth/me` - Get current user

**Acceptance Criteria:**
- ✅ Password hashed (never stored plaintext)
- ✅ JWT token generation on login
- ✅ Token validation middleware works
- ✅ Error handling (duplicate username, invalid credentials)
- ✅ All endpoints match API_SPECIFICATION.md

**Prompt for CloudCode:**
```
Crea gli endpoint di autenticazione per Kilter Up.

File: backend/routes/auth.py

Endpoints:
1. POST /auth/register
   - Input: username, email, password, skill_level
   - Output: user_id, username, token
   - Error: duplicate username/email, validation

2. POST /auth/login
   - Input: email, password
   - Output: user_id, token, expires_in
   - Error: invalid credentials

3. GET /auth/me
   - Protected endpoint
   - Output: user full profile
   - Error: unauthorized

Requisiti:
- Use bcrypt per password hashing
- Use PyJWT per JWT tokens
- Token valid 24 hours
- Proper error responses (400, 401, etc)
- Input validation su email format
```

---

#### Task 1.3: Database Setup & Alembic Migrations
**Deliverable:** Alembic setup + initial migration  
**Files:**
- `alembic/versions/001_initial_schema.py`
- `alembic/env.py` (configure)
- `.env.example` (database URL)

**Acceptance Criteria:**
- ✅ `alembic init` done
- ✅ Migration files auto-generated from models
- ✅ Migration can be applied: `alembic upgrade head`
- ✅ Migration can be rolled back: `alembic downgrade -1`
- ✅ Docker Postgres running locally

**Prompt for CloudCode:**
```
Setup Alembic migrations per Kilter Up.

1. Initialize Alembic in backend/
2. Configure alembic/env.py per SQLAlchemy models
3. Generate initial migration from models
4. Test: migration up, migration down
5. Create docker-compose.yml per PostgreSQL locale

Ordine:
- backend/alembic/env.py
- backend/alembic/versions/001_initial.py
- docker-compose.yml (postgres:15)

Assicurati che migration supporta JSONB type.
```

---

### Tuesday (Feb 19) - Video Upload & Processing

#### Task 2.1: Video Upload Endpoint
**Deliverable:** `backend/routes/video.py` - POST `/videos/upload`  

**Acceptance Criteria:**
- ✅ Accepts multipart form-data (video file)
- ✅ Validates file: MP4, <100MB, <2 min duration
- ✅ Stores file locally (dev) or S3 (later)
- ✅ Creates VideoUpload record in DB with status="processing"
- ✅ Returns upload_id for polling

**Prompt for CloudCode:**
```
Crea endpoint POST /videos/upload

Requisiti:
1. Accept multipart/form-data
   - file (required, video, <100MB)
   - gym_name (optional, string)
   - notes (optional, string)

2. Validate:
   - File is MP4 format
   - File < 100MB
   - Video duration < 2 minutes (use ffprobe)

3. Store:
   - Save file to ./videos_uploaded/ (dev)
   - Extract video duration with FFmpeg
   - Create VideoUpload record: status="processing"

4. Response: (202 Accepted)
   - upload_id
   - status: "processing"
   - estimated_processing_time_seconds

5. Error handling:
   - 400: invalid file
   - 413: file too large
   - 422: bad duration

Non fare video processing adesso - solo upload.
```

---

#### Task 2.2: FFmpeg Integration (Video Frame Extraction)
**Deliverable:** `backend/services/video_processor.py`  

**Acceptance Criteria:**
- ✅ Extract frames from video (1 frame per 0.5 sec)
- ✅ Save frames as JPEG in temp directory
- ✅ Return list of frame files
- ✅ Handle errors (corrupted video, etc)

**Prompt for CloudCode:**
```
Crea video_processor.py per estrarre frames.

Funzione: extract_frames(video_path: str, interval_sec: float = 0.5) -> List[str]

Requisiti:
1. Use FFmpeg (subprocess)
2. Extract 1 frame every 0.5 seconds
3. Save frames as JPEG in ./temp_frames/
4. Return list of frame file paths
5. Clean up temp files after use
6. Handle errors (return empty list if fails)

Comando FFmpeg da usare:
ffmpeg -i {video} -vf "fps=1/{interval_sec}" ./temp_frames/frame_%04d.jpg

Test: extract_frames(test_video.mp4) should return >=30 frames for 15sec video
```

---

#### Task 2.3: Video Status Polling Endpoint
**Deliverable:** `backend/routes/video.py` - GET `/videos/{id}`  

**Acceptance Criteria:**
- ✅ Returns current status ("processing", "success", "failed")
- ✅ If processing, returns progress estimate
- ✅ If success, includes detected_circuit_id + holds data
- ✅ Matches API_SPECIFICATION.md

**Prompt for CloudCode:**
```
Crea GET /videos/{id} endpoint per status polling.

Requisiti:
1. Get VideoUpload record by ID
2. Return:
   - status (processing/success/failed)
   - progress_percent (if processing)
   - detected_circuit_id (if success)
   - detected_holds JSONB (if success)
   - error message (if failed)

3. Validation:
   - Only owner can view own videos
   - 404 if video not found

Response match API_SPECIFICATION.md
```

---

### Wednesday (Feb 20) - Gemini Vision Integration

#### Task 3.1: Gemini Vision API Wrapper
**Deliverable:** `backend/services/gemini_service.py`  

**Acceptance Criteria:**
- ✅ Authenticate with Gemini Vision API
- ✅ Send image frames to API
- ✅ Parse response (holds, difficulty, confidence)
- ✅ Error handling (rate limits, API errors)
- ✅ Environment variable for API key

**Prompt for CloudCode:**
```
Crea gemini_service.py per Gemini Vision API.

Funzione: analyze_frame(image_path: str) -> dict

Requisiti:
1. Use google.generativeai library
2. API key from environment: GEMINI_API_KEY
3. Send frame image to Gemini Vision
4. Prompt (vedi sotto)
5. Parse response JSON
6. Return: {holds[], difficulty, confidence}

Prompt per Gemini:
"Analizza questo frame di Kilterboard:
1. Identifica i hold colorati (rosso/blu/giallo/verde)
2. Descrivi posizionamento (alto/basso, left/right)
3. Infer grip type (jug, sloper, crimp, etc)
4. Difficulty guess: V0-V15
5. Confidence score 0-100%

Output JSON: {holds: [{color, position, grip_type}], difficulty: 'V5', confidence: 85}"

Error handling:
- Retry 3 times su rate limit
- Return empty holds se API fails
```

---

#### Task 3.2: Circuit Detection & BoardLib Matching
**Deliverable:** `backend/services/boardlib_service.py`  

**Acceptance Criteria:**
- ✅ Download BoardLib database locally (CLI command)
- ✅ Load circuit data from SQLite database
- ✅ Match detected holds against known circuits
- ✅ Return top 3 matches with confidence scores

**Prompt for CloudCode:**
```
Crea boardlib_service.py per integrazione BoardLib.

Requisiti:
1. Install: pip install boardlib
2. Download database: boardlib database kilter
3. Load circuits.db SQLite file
4. Function: find_matching_circuits(detected_holds: List[dict]) -> List[dict]

Match algorithm:
- Compare hold colors + positions
- Count matches / total holds
- Confidence = matches / total
- Return top 3 circuits con confidence > 70%

Output format:
[{
  "boardlib_id": 1234,
  "name": "Circuit Name",
  "difficulty": "V5",
  "confidence": 0.87
}]

Fallback: Se no match trovato, return empty list
```

---

#### Task 3.3: Video Analysis Background Job
**Deliverable:** `backend/jobs/video_analysis_job.py`  
**Framework:** Celery + Redis (or simple threading for MVP)

**Acceptance Criteria:**
- ✅ Process video in background (non-blocking)
- ✅ Extract frames → Gemini analysis → Circuit matching
- ✅ Update VideoUpload record with results
- ✅ Handle errors gracefully (mark as failed)

**Prompt for CloudCode:**
```
Crea job per video analysis (background processing).

Per MVP, usa threading non Celery (più semplice).

Workflow:
1. Receive upload_id
2. Get video file path
3. extract_frames() → get frames list
4. For each frame:
   - analyze_frame() con Gemini
   - Extract holds data
5. aggregate_holds() → most common holds across frames
6. find_matching_circuits() → match con BoardLib
7. Update VideoUpload:
   - detected_circuit_id
   - detection_confidence
   - detected_holds JSONB
   - status = "success"
8. On error: status = "failed", error message

Execution:
- Run in background thread
- Update DB status at each step
- Log progress

Non bloccare upload endpoint.
```

---

### Thursday (Feb 21) - Frontend: Upload UI + Circuit Viewer

#### Task 4.1: Video Upload UI Component
**Deliverable:** `app/upload/page.tsx` + `components/VideoUpload.tsx`  

**Acceptance Criteria:**
- ✅ File picker (drag-drop + click)
- ✅ File validation on frontend (MP4, <100MB)
- ✅ Upload progress bar
- ✅ Optional fields: gym_name, notes
- ✅ Returns upload_id on success
- ✅ Responsive design (mobile-friendly)

**Prompt for CloudCode:**
```
Crea UI per video upload.

File: app/upload/page.tsx

Requisiti:
1. Drag-drop zone (grande, visible)
2. Or click to browse files
3. Validate:
   - File type = MP4
   - Size < 100MB
   - Show error se fails
4. Upload progress:
   - Progress bar
   - Upload speed
   - Time remaining
5. On success:
   - Show upload_id
   - "Processing..." message
   - Button: "Check Status"

Components:
- VideoUploadZone (reusable)
- ProgressBar
- ErrorAlert

Styling: Tailwind CSS, dark mode
```

---

#### Task 4.2: Polling & Status Display
**Deliverable:** `components/UploadStatus.tsx`  

**Acceptance Criteria:**
- ✅ Poll `/videos/{id}` every 2 seconds
- ✅ Display progress (% analyzed frames)
- ✅ Show detected circuit when ready
- ✅ Button to view circuit details

**Prompt for CloudCode:**
```
Crea component per polling video status.

File: components/UploadStatus.tsx

Props: upload_id: string

Requisiti:
1. Poll GET /videos/{upload_id} every 2 sec
2. Display:
   - Current status (processing/success/failed)
   - Progress bar (analyzed_frames / total_frames)
   - Estimated time remaining
3. If success:
   - Show "Detected: [Circuit Name]"
   - Confidence score
   - Button: "View Circuit" → navigate to circuit page
4. If failed:
   - Show error message
   - Button: "Upload Again"
5. Stop polling se success o failed

Styling: Match homepage design (orange theme)
```

---

#### Task 4.3: Circuit Viewer Component
**Deliverable:** `components/CircuitViewer.tsx`  

**Acceptance Criteria:**
- ✅ Display circuit holds in visual format
- ✅ Show hold colors, positions, grip types
- ✅ Display difficulty, estimated time, avg rating
- ✅ Responsive grid layout

**Prompt for CloudCode:**
```
Crea component per visualizzare circuito.

File: components/CircuitViewer.tsx

Props: circuit: Circuit (data structure)

Requisiti:
1. Visual representation:
   - 5x4 grid (Kilter board is ~20 holds)
   - Colored circles per hold (red/blue/yellow/green)
   - Hover: show grip type + position
2. Info panel:
   - Name, difficulty, style
   - Estimated time
   - Average rating + ascent count
   - Hold breakdown (jugs/slopers/crimps %)
3. Actions:
   - Add to library button
   - Add to training plan button
   - Share button
4. Responsive:
   - Desktop: grid + side panel
   - Mobile: stacked layout

Styling: Kilter-like, dark background, bright colors
```

---

### Friday (Feb 22) - Integration Testing & Debugging

#### Task 5.1: End-to-End Testing
**Scope:** Video upload → detection → display circuit

**Test Scenarios:**
1. Upload valid video → Detect circuit → Display results
2. Upload invalid file → Show error
3. Upload large file → Show size error
4. Polling timeout → Graceful fallback

**Acceptance Criteria:**
- ✅ Happy path works end-to-end
- ✅ Error cases handled
- ✅ No console errors
- ✅ Responsive on mobile

**Manual Tests:**
```bash
# Backend running
cd backend && uvicorn main:app --reload

# Frontend running
cd app && npm run dev

# Test scenario:
1. Open http://localhost:3000/upload
2. Upload test video
3. See processing status
4. Wait for detection
5. View circuit details
```

---

#### Task 5.2: Bug Fixes & Performance Optimization
**Focus Areas:**
- Video processing speed (<3 sec target)
- API error handling
- Frontend responsiveness
- Database queries (use indexes)

**Checklist:**
- ✅ No N+1 queries
- ✅ API responses <500ms
- ✅ Video analysis <3 sec
- ✅ UI renders <2 sec
- ✅ No unhandled promise rejections

---

## 📊 Success Criteria (Week 1 Complete)

### Functional
- ✅ User can register + login
- ✅ User can upload video
- ✅ Backend processes video in background
- ✅ Gemini Vision analyzes frames
- ✅ Circuit matching works (>80% accuracy on test videos)
- ✅ Frontend displays detected circuit

### Performance
- ✅ Video analysis <3 sec (async)
- ✅ API responses <500ms
- ✅ Page load <2 sec

### Code Quality
- ✅ No crashes on happy path
- ✅ Proper error handling
- ✅ Type hints throughout
- ✅ Docstrings on all functions
- ✅ Tests for critical paths

### Integration
- ✅ Frontend ↔ Backend communication working
- ✅ Database operations stable
- ✅ Gemini Vision integration tested

---

## 🎯 CloudCode Discussion Topics

**Q1:** Should we use Celery for background jobs or threading for MVP?  
→ **Answer:** Threading for MVP (simpler), Celery later

**Q2:** Store videos locally or S3?  
→ **Answer:** Local for MVP (`./videos_uploaded/`), S3 later

**Q3:** Database migration strategy?  
→ **Answer:** Alembic from day 1 (easy to reset in dev)

**Q4:** How to handle Gemini Vision rate limits?  
→ **Answer:** Retry with exponential backoff, queue if needed

**Q5:** Test data for video processing?  
→ **Answer:** Use sample video files; create test suite

---

## 📅 Timeline Summary

```
MON: Database models + Auth endpoints
TUE: Video upload + FFmpeg integration
WED: Gemini Vision + Circuit matching + Background job
THU: Frontend upload UI + Status polling + Circuit viewer
FRI: Integration testing + Bug fixes

Week End: ✅ Video detection working end-to-end
```

---

**Document prepared by:** Sam  
**Status:** Ready for CloudCode planning session  
**Date:** 18/02/2026

