# 🎪 KILTER UP - Piano di Implementazione Completo

> ⚠️ DOCUMENTO OBSOLETO — scritto prima del pivot strategico del 21/02/2026.
> La strategia corretta è in CLAUDE.md e PROJECT_STATUS.md.
> **VIDEO FORM ANALYSIS = CORE.** Circuit recognition = Phase 2 supplementare.
> Questo file è un backlog storico, NON la roadmap attiva.

**Data:** 18 Febbraio 2026
**Versione:** 1.0 - Planning Phase  
**Status:** In Development (Brainstorming & Architecture)

---

## 📋 Sommario Esecutivo

**KILTER UP** è un'app AI-powered per Kilterboard che combina:
1. **Video Analysis** - Riconoscimento automatico del circuito dai video
2. **AI Circuit Generator** - Creazione di circuiti personalizzati
3. **Training Intelligence** - Piani di allenamento adattivi

**Differenziali vs Climbology/Climbdex:**
- ✨ Video recognition (non solo database lookup)
- ✨ Real-time biomechanics feedback
- ✨ Adaptive training plans basati su ML
- ✨ Social features (share circuiti, competizioni)

---

## 🏗️ Architettura Tecnica

### Frontend (Next.js 14 + TypeScript + Tailwind)
```
kilter-training-app/
├── app/
│   ├── page.tsx              # Homepage (✅ già fatta)
│   ├── upload/               # Video upload + processing
│   ├── circuits/             # Circuit gallery & details
│   ├── generate/             # AI circuit generator
│   ├── training/             # Training plans
│   └── analytics/            # Performance tracking
├── components/
│   ├── VideoPlayer.tsx       # Video viewer con overlay
│   ├── CircuitViewer.tsx     # Visualizza circuito
│   ├── HoldAnalyzer.tsx      # Hold-by-hold breakdown
│   └── TrainingPlan.tsx      # Piano settimanale
├── lib/
│   ├── gemini-vision.ts      # Gemini Vision API wrapper
│   ├── boardlib.ts           # BoardLib wrapper
│   └── ml-models.ts          # ML inference utils
└── hooks/
    ├── useCircuitDetection.ts
    ├── useTrainingPlan.ts
```

### Backend (Python FastAPI)
```
backend/
├── main.py                    # FastAPI app
├── routes/
│   ├── video.py              # Upload, process video
│   ├── circuits.py           # Circuit CRUD + search
│   ├── generator.py          # AI circuit generation
│   └── training.py           # Training plans
├── services/
│   ├── gemini_service.py     # Gemini Vision calls
│   ├── boardlib_service.py   # BoardLib integration
│   ├── ml_service.py         # ML model inference
│   └── video_processor.py    # Video frame extraction
├── models/
│   ├── circuit.py
│   ├── user.py
│   └── training_log.py
├── db/
│   └── database.py           # SQLAlchemy setup
└── requirements.txt
```

---

## 🚀 Features Prioritizzate (MVP)

### Phase 1: Core Video + Circuit Recognition (Settimane 1-2)
- [ ] **Video Upload Interface** - File picker, progress bar, validation
- [ ] **Gemini Vision Integration** - Analisi frame video per riconoscere hold layout
- [ ] **BoardLib Integration** - Match automatico con circuiti noti
- [ ] **Circuit Viewer** - Visualizzazione del circuito riconosciuto
- [ ] **Accuracy Feedback** - % di match con circuiti reali

**Input:** Video MP4 (1-2 min, portrait)  
**Output:** Circuito identificato + statistiche  
**Success:** <2s per analizzare video; 85%+ accuracy su circuiti mainstream

---

### Phase 2: AI Circuit Generator (Settimane 2-3)
- [ ] **Generator UI** - Slider per difficoltà, muscoli target, stile
- [ ] **ML Model** - Trained su BoardLib database per predire circuiti
- [ ] **Hold Suggestion** - Suggerisce sequenze logiche
- [ ] **Difficulty Prediction** - Stima grade prima di climbare
- [ ] **Export as Image** - PNG da stampare/condividere

**Input:** Difficulty (V0-V10), Muscle Focus, Style (power/endurance/technique)  
**Output:** 3-5 circuiti suggeriti + spiegazione per hold  
**Success:** Circuiti generati sono "climbable" e diversificati

---

### Phase 3: Training Intelligence (Settimana 3+)
- [ ] **Progress Tracking** - Log ascensioni, tempi, RPE (1-10)
- [ ] **Adaptive Plans** - Genera piano settimanale in base a skill
- [ ] **Weakness Detection** - Identifica tipi di problemi dove fai fatica
- [ ] **Dashboard** - Stats: ascensioni/week, grade distribution, muscoli usati
- [ ] **Recommendations** - "Fai più jugs questa week", "Prova endurance circuit"

**Input:** Training history + stats personali  
**Output:** Piano settimanale personalizzato  
**Success:** Climber vede improvement in 4 settimane

---

## 🔌 Integrazioni Critiche

### 1. **Gemini Vision API**
```python
# Prompt per frame analysis
prompt = """
Analizza questo frame di un Kilterboard:
1. Identifica i hold colorati (rosso, blu, giallo, verde)
2. Descrivi la layout (angoli, posizionamento)
3. Se riconosci un pattern, suggerisci quale circuito potrebbe essere
4. Confidence score (0-100%) per la predizione
"""
```

### 2. **BoardLib API**
```python
# Scarica database circuiti Kilter
from boardlib import KilterBoard
board = KilterBoard()
circuits = board.get_all_circuits()
# Access: circuits[i].difficulty, .holds, .ascents, etc
```

### 3. **ML Model Training**
- **Dataset:** BoardLib database (10k+ circuiti)
- **Features:** Hold positions, difficulty, grade, style
- **Model:** LightGBM per difficulty prediction + similarity search
- **Input:** Hold layout → Output: Likely difficulty range

---

## 📊 Database Schema (SQLAlchemy)

```python
# User
class User(Base):
    id, email, username, skill_level, preferences

# Circuit (custom + generated)
class Circuit(Base):
    id, created_by, name, holds[], difficulty, 
    grade, description, source ("kilter"/"generated"/"custom")

# Video Upload
class VideoUpload(Base):
    id, user_id, file_path, detected_circuit_id,
    confidence, processed_at, metadata {}

# Training Log
class TrainingLog(Base):
    id, user_id, circuit_id, completed, rpe (1-10),
    time_taken_sec, notes, video_url

# TrainingPlan
class TrainingPlan(Base):
    id, user_id, week_start, 
    circuits[], recommendations[], generated_by_ai
```

---

## 🎯 Roadmap Dettagliato

### Week 1: Foundation
- [x] Setup Next.js + FastAPI (✅ Done)
- [ ] Database schema + SQLAlchemy models
- [ ] BoardLib Python wrapper + database sync
- [ ] Video upload endpoint (S3/local storage)

### Week 2: Video → Circuit Recognition
- [ ] Gemini Vision integration for hold detection
- [ ] Frame extraction from video (FFmpeg)
- [ ] Similarity matching con BoardLib circuits
- [ ] CircuitViewer component
- [ ] Frontend for upload + results

### Week 3: AI Circuit Generator
- [ ] ML model training on BoardLib data
- [ ] Generator API endpoint
- [ ] UI con sliders + suggestions
- [ ] Hold sequence visualization
- [ ] Difficulty prediction

### Week 4: Intelligence + Polish
- [ ] Training log schema + tracking UI
- [ ] Adaptive plan generation
- [ ] Dashboard + analytics
- [ ] Social sharing (JSON export)
- [ ] Testing + optimization

---

## 💡 Innovative Ideas (Beyond MVP)

### Short-term (settimane 4-6)
1. **Leaderboards** - "Best circuits this week" per difficulty
2. **Collaboration** - Climbers editano circuiti insieme
3. **Mobile App** - React Native per iOS/Android
4. **Workout Tracking** - Integrazione con Strava/Apple Health

### Medium-term (mesi 2-3)
1. **Real-time Feedback** - Webcam + skeleton tracking durante climb
2. **AR Circuit Preview** - Vedi circuito sovrapposto al muro reale
3. **Coach Mode** - Dashboard per allenatori con club di climber
4. **API Marketplace** - Third-party apps su dati Kilter Up

### Long-term (visione)
1. **Gym B2B** - Integrare con gym software per manage circuiti
2. **Kilter Board Integration** - Mandare circuiti direttamente al tabellone
3. **AI Difficulty Calibration** - Migliora grading in tempo reale basato su ascensioni

---

## 🛠️ Tech Decisions

| Aspetto | Scelta | Perché |
|---------|--------|-------|
| Frontend | Next.js 14 | Fast, SSR pronto, TypeScript |
| Backend | FastAPI | Async, Python per ML/CV |
| Video Processing | FFmpeg | Open source, reliable |
| Vision AI | Gemini Vision | Free tier + good quality |
| ML | LightGBM | Lightweight, interpretabile |
| Database | PostgreSQL | Relational, scalable |
| Storage | Local (dev) → S3 (prod) | Semplice e economico |
| Deploy | Vercel (frontend) + Heroku/Railway (backend) | Free tier generous |

---

## 🚨 Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Gemini Vision accuracy basso | Feature inutilizzabile | Test su 100 video reali; fallback a manual |
| BoardLib API changes | Code breaks | Monitor GitHub; version lock |
| ML model underfitting | Generator mediocre | Data augmentation; ensemble models |
| Slow video processing | Poor UX | Async processing + progress indication |
| Storage costs (S3) | 💰 Expensive | Compress videos; delete old uploads |

---

## ✅ Success Criteria

### MVP Completion (Week 4)
- ✅ Video upload + detection working >80% accuracy
- ✅ AI generator creates unique valid circuits
- ✅ Training log stores data correttamente
- ✅ Dashboard mostra stats basiche
- ✅ No crashes, basic error handling

### Launch Ready (Week 5+)
- ✅ Polished UI/UX
- ✅ Fast performance (<3s per video analysis)
- ✅ 10+ test users, positive feedback
- ✅ Deployed + accessible online
- ✅ Documentation complete

---

## 📚 References & Inspiration

1. **BoardLib** - https://github.com/lemeryfertitta/BoardLib
2. **Climbology** - https://github.com/Rundstedtzz/climbology (AI beta design)
3. **Belay AI** - Biomechanics analysis reference
4. **Climbdex** - https://github.com/lemeryfertitta/Climbdex (search engine)

---

## 🎨 Design Philosophy

**"Climbers first, complexity second"**

- Every feature serves the climber's training goal
- Simple, not simplistic
- Visual > textual (drawings > words)
- Gamification (badges, streaks) but not distracting
- Mobile-first responsive design

---

**Autore:** Sam + Daniele  
**Revisione:** 18/02/2026 10:00 CET  
**Next Step:** CloudCode planning discussion → Definire sprint 1 in dettaglio
