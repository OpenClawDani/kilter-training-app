# Kilter-Up — Roadmap Attiva
> Aggiornato: 12 marzo 2026
> Strategia: VIDEO FORM ANALYSIS = CORE

## Stato attuale
- Backend: FastAPI + SQLite (dev) / PostgreSQL (prod)
- Auth JWT: ✅ funzionante
- Video upload + Gemini analysis: ✅ funzionante
- Frontend upload UI: ✅ funzionante (drag-drop, progress bar)
- Deploy: non ancora fatto

## Phase 2 — Training Logs (prossima)
- [ ] Schema training_logs nel DB
- [ ] Alembic migration 003
- [ ] Endpoint POST /training-logs
- [ ] Endpoint GET /training-logs
- [ ] Frontend: log sessione dopo analisi video
- [ ] Tests pytest

## Phase 3 — Circuit Logger (BoardLib, supplementare)
- [ ] BoardLib API integration
- [ ] Foto circuito LED → riconosce circuito
- [ ] Quick log "ho fatto questo circuito"
- [ ] NON è il differenziale principale

## Phase 4 — Dashboard + Deploy
- [ ] Dashboard analytics (grade distribution, RPE trend, streak)
- [ ] Deploy: Railway (backend) + Vercel (frontend)
- [ ] PostgreSQL su Railway
- [ ] S3 per storage video

## Phase 5 — Polish
- [ ] Mobile responsive
- [ ] Notifiche / achievements
- [ ] Social sharing circuiti

## Regole non negoziabili
- Gemini File API (NON frame-by-frame)
- FastAPI BackgroundTasks (NON Celery/Redis)
- Test pytest obbligatori per ogni endpoint
- Secrets solo in .env
