# 🧗 Claude Code Guidelines - Kilter-Up App

## Project Overview
**Kilter-Up** — AI-powered climbing form analysis app.

**Core Value Proposition:**
- Upload a climbing video → extract a fragment → Gemini Vision analyzes your form → get actionable feedback
- NOT a circuit recognition app. Form analysis is the core.

**Primary Tech Stack:**
- Frontend: Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
- Backend: Python 3.11 + FastAPI + PostgreSQL + SQLAlchemy + Alembic
- AI: Gemini Vision API (form analysis)
- Circuit recognition: BoardLib API (supplementary only)
- Storage: Local filesystem (dev) → S3 (prod, week 3)

## 🎯 CORE STRATEGY (Non-Negotiable)

```
🎥 VIDEO = CORE FEATURE
  Upload video → extract fragment (trim/stabilize)
  → Gemini Vision → form analysis
  → Output: "V5 in 45s, form solid, weak finish on sloper"

📸 PHOTO = UTILITY (supplementary, Phase 2)
  Quick LED recognition (BoardLib) for logging
  → NOT the main value driver
```

**Gemini Vision analyzes:**
- Hold positions and quality
- Body tension and posture
- Efficiency score
- Specific weaknesses (e.g., "weak on sloper finish")
- Grade estimate

---

## 📦 Current State (Day 2 Complete)

✅ **Day 1:** FastAPI backend + Docker setup
✅ **Day 2:** Auth system (JWT) + User model + VideoUpload model (needs update)

**Day 3 Goal:** Video upload endpoint + Gemini Vision integration

---

## Core Rules for Claude Development

### 📋 Code Standards
- **Language**: English for code, Italian for comments when needed
- **Style**: Follow PEP 8 (Python), ESLint (TypeScript)
- **No secrets in code**: Use environment variables for API keys
- **Type safety**: Always use TypeScript types, Python type hints

### ✅ ALWAYS Do This
1. **Write tests for every feature** — pytest (backend), Jest (frontend)
2. **Test locally before push** — full suite must pass
3. **Commit with clear messages**: `feat: add video upload endpoint`
4. **Push after each working feature** — small, atomic commits
5. **Document complex logic** — docstrings for functions

### ❌ NEVER Do This
1. Commit broken code
2. Push credentials, API keys, or .env files
3. Change database schema without creating a new Alembic migration
4. Skip tests
5. Add circuit detection as a primary feature (it's Phase 2)

---

## 🏗️ Project Structure

```
kilter-training-app/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── auth.py             ✅ (JWT auth)
│   │   │   ├── videos.py           🔲 (video upload + analysis)
│   │   │   └── sessions.py         🔲 (session CRUD)
│   │   ├── core/
│   │   │   ├── config.py           ✅
│   │   │   ├── database.py         ✅
│   │   │   ├── security.py         ✅
│   │   │   └── deps.py             ✅
│   │   ├── models/
│   │   │   ├── user.py             ✅
│   │   │   └── video.py            🔄 (needs update for form analysis)
│   │   ├── schemas/
│   │   │   ├── user.py             ✅
│   │   │   ├── auth.py             ✅
│   │   │   └── video.py            🔲 (new)
│   │   ├── services/
│   │   │   ├── auth_service.py     ✅
│   │   │   ├── gemini_service.py   🔲 (Gemini Vision wrapper)
│   │   │   ├── video_service.py    🔲 (ffmpeg fragment extraction)
│   │   │   └── storage_service.py  🔲 (local + S3)
│   │   └── main.py                 ✅
│   ├── alembic/                    ✅
│   ├── tests/
│   │   ├── test_auth_validation.py ✅
│   │   └── test_videos.py          🔲 (new)
│   └── requirements.txt
├── frontend/ (Next.js 14)
│   └── app/
│       ├── page.tsx                ✅ (homepage)
│       ├── upload/page.tsx         🔲
│       ├── session/[id]/page.tsx   🔲
│       └── dashboard/page.tsx      🔲
└── CLAUDE.md
```

---

## 🔧 Useful Commands

```bash
# Backend
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8001
pytest                    # Run all tests
pytest --cov             # Coverage report
alembic upgrade head     # Apply migrations

# Frontend
npm run dev
npm test
npm run build
npm run lint

# Git
git status && git diff
git add . && git commit -m "feat: description"
git push origin main
```

---

## 🧪 Testing Requirements
- **Backend:** pytest, >80% coverage on new code
- **Frontend:** Jest + React Testing Library
- All tests must pass before push

---

## 🎬 Development Flow
1. **Receive task** → Understand scope
2. **Plan** → Files to change + dependencies
3. **Code** → Implement + tests
4. **Verify** → Full test suite green
5. **Commit** → Clear message
6. **Push** → Confirm push succeeded

---

**Version:** 2.0 (strategy updated 2026-02-21 — VIDEO = CORE)
**Owner:** Daniele Somensi + Sam (AI Agent)
