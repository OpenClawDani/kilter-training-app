# 📋 KILTER-UP — Project Status & Decisions Log

> **Questo file è la fonte di verità del progetto.**
> Aggiornato da Sam ogni volta che si prende una decisione importante.
> Leggi questo PRIMA di fare qualsiasi cosa sul progetto.

---

## 🗓️ Ultimo Aggiornamento: 22 Febbraio 2026

---

## 📊 STATO ATTUALE

| Componente | Status | Note |
|------------|--------|------|
| Backend FastAPI | ✅ Done | Auth JWT funzionante, SQLite |
| Auth (JWT) | ✅ Done | Register, login, token |
| User model + migrations | ✅ Done | Alembic setup |
| VideoUpload model | 🔄 Da aggiornare | Needs schema for Gemini results |
| Gemini Video Service | ⏳ Da fare | **PROSSIMO STEP** |
| Video upload endpoint | ⏳ Da fare | POST /api/videos/upload |
| Frontend upload UI | ⏳ Da fare | Next.js drag-drop |
| Training logs | ⏳ Da fare | Phase 2 |
| Circuit logger (BoardLib) | ⏳ Da fare | Phase 2 — SUPPLEMENTARE |
| Dashboard | ⏳ Da fare | Phase 3 |
| Deploy (Railway + Vercel) | ⏳ Da fare | Phase 4 |

---

## 🎯 CORE STRATEGY (Non si discute)

```
🎥 VIDEO = CORE FEATURE (priorità assoluta)
   Upload video → Gemini Video API → form analysis
   Output: "V5, body tension ok, weak on sloper finish"

📸 PHOTO = UTILITY (supplementare, Phase 2)
   BoardLib API per quick circuit logging
   NON è il differenziale principale
```

---

## 🔑 CREDENZIALI & CONFIG

| Variabile | Valore | Note |
|-----------|--------|------|
| `GEMINI_API_KEY` | Già in `.env` ✅ | AIzaSyCB... |
| `DATABASE_URL` | `sqlite:///./kilter.db` | Dev locale |
| `JWT_SECRET` | Già in `.env` ✅ | Generato |
| `UPLOAD_DIR` | `uploads/` | Locale |
| GitHub | `OpenClawDani/kilter-training-app` | Main repo |

---

## 🐛 PROBLEMI RISOLTI (non ripetere gli errori!)

### ❌ PROBLEMA 1: Frame-by-frame analysis = rate limit
**Quando:** Day 3 planning (19-21 Feb 2026)
**Problema:** Il piano originale mandava ogni frame del video come immagine separata a Gemini. 30 secondi di video @ 1 FPS = 30 API calls → rate limit del free tier (15 req/min) → 2 minuti di attesa.
**Soluzione:** ✅ **Gemini File API** — upload il video intero UNA volta, poi UNA sola chiamata a Gemini con `file_data`. Gemini elabora internamente tutti i frame.

**Implementazione corretta:**
```python
import google.generativeai as genai

# Step 1: Upload video (una volta)
video_file = genai.upload_file(path="climbing_video.mp4")

# Step 2: Aspetta che il file sia processato
while video_file.state.name == "PROCESSING":
    video_file = genai.get_file(video_file.name)

# Step 3: UNA sola chiamata di analisi
model = genai.GenerativeModel("gemini-2.0-flash")
response = model.generate_content([
    video_file,
    "Analizza la tecnica di arrampicata in questo video..."
])
```

**DON'T DO THIS:**
```python
# ❌ SBAGLIATO - frame per frame
for frame in frames:
    response = genai.generate_content([frame, prompt])  # 30 API calls!
```

---

### ❌ PROBLEMA 2: PostgreSQL → SQLite migration
**Quando:** Day 2 sprint (19 Feb 2026)
**Problema:** Setup iniziale con PostgreSQL aveva problemi di compatibilità UUID su macOS dev.
**Soluzione:** ✅ Switchato a SQLite per dev locale (String(36) per UUID), PostgreSQL per production.
**File:** `backend/app/models/user.py`, `backend/app/models/video.py`

---

## ✅ DECISIONI ARCHITETTURALI PRESE

### 1. Gemini 2.0 Flash (non MediaPipe/YOLO)
**Decisione:** Usare Gemini Vision API per MVP invece di MediaPipe + YOLO.
**Perché:**
- Zero ML training richiesto → MVP più veloce
- Gemini capisce il contesto climbing senza dataset custom
- MediaPipe/YOLO possono essere aggiunti in Phase 2 per accuracy
- Costo irrisorio: ~$0.001 per video analizzato

### 2. FastAPI + SQLite (dev) / PostgreSQL (prod)
**Decisione:** Backend Python perché l'ML ecosystem è Python-first.
**Perché:** MediaPipe, YOLO, google-generativeai sono tutti Python.

### 3. Video = async processing
**Decisione:** Upload video → 202 Accepted → job in background → polling status.
**Perché:** Video processing può durare 10-30 secondi, non bloccare la UI.

### 4. Storage: Locale (dev) → S3 (prod)
**Decisione:** Local filesystem per dev, S3 per production.
**Perché:** Semplicità dev, scalabilità prod.

### 5. NO Celery/Redis per MVP
**Decisione:** Background task con FastAPI `BackgroundTasks` (built-in), non Celery.
**Perché:** Celery aggiunge complessità (Redis dependency). FastAPI BackgroundTasks è sufficiente per MVP.

---

## 🗺️ ROADMAP

### ✅ Phase 1 — Foundation (Done)
- FastAPI backend
- Auth JWT
- Database setup

### 🎯 Phase 2 — Video Analysis (PROSSIMO)
**Obiettivo:** Upload video → Gemini analizza → feedback form

**Tasks:**
1. Aggiorna VideoUpload model (schema per Gemini results)
2. Crea Alembic migration 002
3. Implementa `gemini_service.py` (Gemini File API + analyze)
4. Implementa `storage_service.py` (salva video localmente)
5. Endpoint `POST /api/videos/upload`
6. Endpoint `POST /api/videos/{id}/analyze`
7. Endpoint `GET /api/videos/{id}` (polling status)
8. Tests (pytest)
9. Frontend: upload UI (drag-drop) + status page

**Acceptance criteria:**
- Upload MP4 → ricevo video_id
- Chiamo /analyze → Gemini processa → ricevo form_feedback
- Frontend mostra il feedback in modo leggibile

### ⏳ Phase 3 — Training Logs
- Log sessioni di arrampicata
- Tracking progressi nel tempo
- Weekly training plan

### ⏳ Phase 4 — Circuit Logger (BoardLib)
- Foto circuito LED → riconosce circuito BoardLib
- Log rapido "ho fatto questo circuito"
- Supplementare al video analysis

### ⏳ Phase 5 — Deploy & Polish
- Railway (backend) + Vercel (frontend)
- Dashboard analytics
- Mobile responsive

---

## 📁 STRUTTURA REPOSITORY

```
kilter-training-app/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py             ✅ JWT auth endpoints
│   │   │   └── videos.py           ⏳ DA FARE
│   │   ├── models/
│   │   │   ├── user.py             ✅
│   │   │   └── video.py            🔄 DA AGGIORNARE
│   │   ├── schemas/
│   │   │   ├── user.py             ✅
│   │   │   └── video.py            ⏳ DA FARE
│   │   ├── services/
│   │   │   ├── auth_service.py     ✅
│   │   │   ├── gemini_service.py   ⏳ DA FARE (usa File API!)
│   │   │   └── storage_service.py  ⏳ DA FARE
│   │   ├── core/
│   │   │   ├── config.py           ✅
│   │   │   ├── database.py         ✅
│   │   │   └── security.py         ✅
│   │   └── main.py                 ✅
│   ├── alembic/
│   │   └── versions/
│   │       ├── 001_initial.py      ✅
│   │       └── 002_video_form.py   ⏳ DA CREARE
│   ├── tests/
│   │   ├── test_auth.py            ✅
│   │   └── test_videos.py          ⏳ DA FARE
│   ├── uploads/                    (gitignored)
│   ├── requirements.txt            🔄 aggiungere google-generativeai
│   └── .env                        ✅ (gitignored, Gemini key inside)
├── app/ (Next.js frontend)
│   └── page.tsx                    ✅ Homepage
├── CLAUDE.md                       ✅ Dev guidelines
├── PROJECT_STATUS.md               ✅ Questo file
├── REPORT_VIDEO_ANALYSIS.md        ✅ Research + feasibility
└── DAY3_CLOUDCODE_PROMPT.md        🔄 Da aggiornare con fix Gemini File API
```

---

## 🧪 COME FARE GIRARE IL PROGETTO (dev)

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8001

# Frontend
npm run dev  # porta 3000

# Test backend
cd backend && pytest -v
```

---

## 📌 REGOLE PER CLAUDE CODE

1. **Leggi questo file PRIMA di iniziare qualsiasi task**
2. **Usa Gemini File API** per video (NON frame-by-frame)
3. **NON aggiungere Celery/Redis** — usa FastAPI BackgroundTasks
4. **NON mettere secrets nel codice** — tutto in `.env`
5. **NON rompere auth esistente** — funziona, non toccarla
6. **Scrivi test** — pytest obbligatorio per ogni nuovo endpoint
7. **Commit piccoli e descrittivi** dopo ogni feature funzionante

---

*Creato da Sam — 22 Febbraio 2026*
*Aggiorna questo file ogni volta che prendi una decisione importante!*
