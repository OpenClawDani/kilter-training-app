# 🎪 KILTER UP - Presentazione Completa
## Piano Dettagliato + Decisioni Tecniche

**Presentazione:** 18 Febbraio 2026, 12:00 CET  
**Durata:** ~30 min discussion  
**Livello:** Ready per CloudCode planning discussion

---

## 🎯 The Pitch (2 min)

**Problema:**
- Climber vuole: salire circuiti, migliorare, seguire un programma
- Status quo: 3 app separate (Kilter ufficiale + search engine + AI beta design)
- Gap: Nessuno integra video recognition + AI generation + adaptive training

**Kilter Up Soluzione:**
- 📱 Carica video → AI riconosce circuito
- 🤖 AI genera circuiti personalizzati
- 📈 App suggerisce training plan adattivo
- 🎮 Gamification + community features

**Differenziale:**
- Video recognition (first-to-market per climbing!)
- Integrated ecosystem (non fragmented)
- Data-driven training (forecasting, not just logging)

---

## 🏗️ Architettura Finale

```
┌─────────────────────────────────────────────────────────┐
│                   KILTER UP ECOSYSTEM                    │
├─────────────────────────────────────────────────────────┤
│                                                           │
│   Frontend (Next.js 14)        Backend (FastAPI)         │
│   ├─ Upload UI                 ├─ Video processing       │
│   ├─ Circuit Gallery           ├─ Gemini Vision API      │
│   ├─ Generator                 ├─ BoardLib integration   │
│   ├─ Training Dashboard        ├─ ML inference           │
│   └─ Analytics                 └─ Database (PostgreSQL)  │
│                                                           │
├─────────────────────────────────────────────────────────┤
│         External APIs                                     │
│   • Gemini Vision (hold detection)                        │
│   • BoardLib (circuit database)                           │
│   • S3 (video storage)                                    │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

**Tech Stack:**
- **Frontend:** Next.js 14, TypeScript, Tailwind CSS, React 18
- **Backend:** Python FastAPI, async/await
- **DB:** PostgreSQL + SQLAlchemy ORM
- **Vision:** Gemini Vision API (free tier)
- **Storage:** S3 (videos), local (dev)
- **ML:** LightGBM (difficulty prediction)
- **Deploy:** Vercel (frontend) + Railway (backend)

---

## 📋 Feature Breakdown (MVP - 4 Settimane)

### 1️⃣ Video Recognition Engine (Week 1-2)
**Goal:** Upload video → Detect circuit automatically

**Workflow:**
```
Video Upload (UI)
    ↓
FFmpeg: Extract frames (every 0.5sec)
    ↓
Gemini Vision: Analyze each frame
    ↓
"This looks like V6 circuit with 4 jugs, 2 slopers"
    ↓
BoardLib Search: Match pattern
    ↓
Result: "Matched to 'Power Circuit #42' (confidence: 87%)"
    ↓
Save + Display
```

**Gemini Prompt:**
```
Analizza questo frame di Kilterboard:
1. Identifica colori dei hold (rosso/blu/giallo/verde)
2. Posizionamento (alto/basso, left/right)
3. Tipo di grip inferito
4. Confidence score per la predizione

Output format: JSON
{
  "holds": [...],
  "difficulty_guess": "V5-V6",
  "confidence": 0.87,
  "similar_patterns": [...]
}
```

**Success Metrics:**
- ✅ <2 sec per analizzare video
- ✅ >85% match rate su circuiti noti
- ✅ Graceful fallback se non riconosciuto

---

### 2️⃣ AI Circuit Generator (Week 2-3)
**Goal:** Create custom circuits based on parameters

**Input Slider Interface:**
```
Difficulty: [V0 ━━━━●━━━━ V10]
Muscolo Focus: [Jug / Sloper / Crimp / All]
Duration: [Quick (3-5 min) / Moderate / Long (10+ min)]
Style: [Power / Endurance / Tech]
```

**ML Model:**
- Trained su 10k+ circuiti da BoardLib
- Features: Hold positions, difficulty, grade, style
- Output: Score per possibili combinazioni di hold

**Generator Flow:**
```
User inputs
    ↓
ML model: Generate top-5 hold sequences
    ↓
Validate: Sequence è "climbable"?
    ↓
Rank: Difficulty prediction
    ↓
Display: 3 suggested circuits + explanations
    ↓
User: Pick one → Save to library
```

**Spiegazione per Hold:**
```
Hold 1: Jugs (good warm-up, comfortable)
Hold 2: Sloper (power focus)
Hold 3: Crimp (weakness training)
...
Overall: This will improve your sloper strength
```

**Success Metrics:**
- ✅ Generated circuits sono climbable
- ✅ Difficulty prediction within 1 grade
- ✅ Diversity: 3 circuits are actually different

---

### 3️⃣ Training Intelligence (Week 3-4)
**Goal:** Adaptive weekly training plans

**Algorithm:**
```
User's last 20 ascensioni
    ↓
Analyze: Grade distribution, muscoli dominanti, success rates
    ↓
Identify: "You're good at jugs, bad at slopers"
    ↓
Plan: "Next week: 60% sloper focus, 40% balanced"
    ↓
Generate: 
  MON: 3x sloper max attempts (V6-V7)
  WED: 4x mixed circuits (endurance)
  FRI: Weakness day (sloper + crimps)
    ↓
Display: Calendar + difficulty breakdown
    ↓
User climbs → Log results
    ↓
Next week: Adapt based on performance
```

**Dashboard Shows:**
- 📊 Grade distribution (# of V5s, V6s climbed)
- 💪 Muscolo usage (pie chart)
- 📈 Progress: "Last week +2 V6 ascensioni"
- 🎯 This week's plan (visual calendar)
- 🔮 Forecast: "At this pace, V7 in 5-6 weeks"

**Success Metrics:**
- ✅ Plan is generated in <5 sec
- ✅ Climbers follow 70% of suggestions (engagement)
- ✅ Measurable improvement in 4 weeks

---

### 4️⃣ Basic Analytics + Tracking (Week 3-4)
**Goal:** Log ascensioni, visualize progress

**Tracking UI:**
```
Circuit: [Auto-selected or search]
Difficulty: [Did you send it?]
RPE: [Rate effort 1-10]
Notes: ["Sloper felt strong", etc]
```

**Dashboard:**
```
This Week:
- 15 ascensioni (3 more than last week)
- Grade avg: V5.2
- Most used muscolo: Jug (60%)
- Favorite gym: [Gym name]

Best Circuits:
- V6 Power (5x ascended)
- V5 Endurance (4x ascended)

Weak Spots:
- Slopers (V4 success rate: 40%)
- Overhangs (V5 success rate: 35%)
```

**Success Metrics:**
- ✅ Logging takes <30 sec
- ✅ All data visualizes correctly
- ✅ Data exports as CSV

---

## 🎮 Gamification (Launch Later, Beta in MVP)

**Simple version in MVP:**
- 🏆 Badge: "First Video Upload"
- 🔥 Streak counter: "Training 5 days"
- 📈 Mini achievement: "Sent V6 this week!"

**Not in MVP (post-launch):**
- ❌ Leaderboards
- ❌ Social remix
- ❌ Advanced badges

---

## 🔄 Data Flow Examples

### Example 1: New User Flow
```
1. User opens app → sees "Upload your first climb"
2. Records 45sec video of circuito in gym
3. Uploads → AI processes (15 sec)
4. Result: "V6 Power Circuit (87% match)"
5. Option: Save or Discard
6. Saved → appears in "My Circuits"
7. Next day: "Train this circuit 2x this week!"
```

### Example 2: Progression Over Weeks
```
Week 1: 8 ascensioni, mostly V5
  Plan: "Build foundation"
Week 2: 12 ascensioni, mix V5-V6
  Plan: "Increase volume"
Week 3: 10 ascensioni, 5x V6, 1x V7
  Plan: "Push grade boundary"
Week 4: 12 ascensioni, consistent V6
  Insight: "You're V6 now! Next target: V7"
```

---

## 📊 Success Criteria (MVP Completion)

### Functional
- ✅ Video upload handles 30-60sec MP4
- ✅ Gemini Vision integration works (real API calls)
- ✅ BoardLib circuits accessible in database
- ✅ Circuit generation produces valid circuits
- ✅ Training log persists to database
- ✅ Weekly plans generate correctly

### Performance
- ✅ Video analysis <3 sec (async background job)
- ✅ Page loads <2 sec
- ✅ Database queries <500ms

### UX/Quality
- ✅ No crashes on happy path
- ✅ Error messages are helpful
- ✅ UI is responsive (mobile + desktop)
- ✅ Dark mode for gym use 😎

### Engagement
- ✅ First 10 test users spend >30min in app
- ✅ Return rate (next day) >60%

---

## 💼 Decision Points (CloudCode Discussion)

**Q1:** Video storage — Local (dev) vs S3 (prod)?
→ Decision: Local for MVP, S3 later

**Q2:** Database — PostgreSQL or SQLite?
→ Decision: PostgreSQL (scalable, free tier on Railway)

**Q3:** ML model — Train from scratch or use pre-trained?
→ Decision: Start with rule-based, add LightGBM if data permits

**Q4:** Gemini Vision rate limit — Free tier enough?
→ Decision: Yes, 50 calls/min should be fine for MVP

**Q5:** Deploy schedule — Weekly sprints or flexible?
→ Decision: Flexible, review Friday + deploy if ready

---

## 📅 Sprint Schedule

```
Week 1 (Feb 18-22):
  MON: Database setup + video upload endpoint
  TUE: Gemini Vision integration
  WED: Circuit viewer component
  THU: BoardLib matching algorithm
  FRI: End-to-end video → detection working

Week 2 (Feb 25-Mar 1):
  MON-WED: AI circuit generator
  THU: Training log basic UI
  FRI: Testing + bug fixes

Week 3 (Mar 4-8):
  MON-WED: Weekly plan generation
  THU: Dashboard + analytics
  FRI: Polish + testing

Week 4 (Mar 11-15):
  MON-TUE: Final bugs + optimization
  WED: Launch (internal test)
  THU-FRI: Feedback + tweaks
```

---

## 🚀 Go-to-Market (Post-MVP)

**Week 1-2 Launch:**
- Closed beta: 10 friends + climbing community
- Feedback collection
- Bug fixes

**Week 3-4 Launch:**
- Public beta: Open to Kilter community
- Marketing: Reddit /r/kilterboard, Discord
- Growth: Referral system

**Month 2+:**
- Premium tier (advanced features)
- Coach tools
- Gym partnerships

---

## 🎯 Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| Gemini Vision accuracy | Test on 50+ real videos; fallback to manual |
| BoardLib API changes | Monitor + version lock; fallback to search |
| Deployment delays | Focus on MVP features only; cut scope if needed |
| Low user engagement | A/B test landing page; adjust value prop |
| Slow video processing | Queue system + async jobs; show progress bar |

---

## 📈 Metrics We'll Track

**Engagement:**
- DAU (daily active users)
- Videos uploaded/user
- Avg session duration
- Return rate (day 1, day 7)

**Performance:**
- Video analysis time (p50, p95)
- API error rate
- Page load time

**Business:**
- Signups
- Conversion to premium (future)
- Retention rate

---

## 💡 Unique Selling Points (Why This Wins)

1. **Video Recognition** — First climbing app with AI hold detection
2. **Integrated** — All-in-one: detect + generate + train
3. **Data-driven** — Real forecasting, not just logging
4. **Community-ready** — Built for social (remix, leaderboards coming)
5. **Open** — Uses open BoardLib API, not proprietary

---

## ❓ Questions for Discussion

1. **Scope ok?** (Is MVP realistic for 4 weeks?)
2. **Tech stack approved?** (Next.js + FastAPI + PostgreSQL?)
3. **Gemini Vision is acceptable?** (Free tier, might have errors)
4. **Timeline — fixed 4 weeks, or flexible?**
5. **Deploy target — local dev, or live?**

---

## 📚 Resources Ready

- ✅ `KILTER_IMPLEMENTATION_PLAN.md` (technical detail)
- ✅ `INNOVATION_BRAINSTORM.md` (ideas + differentials)
- ✅ `CLAUDE.md` (development guidelines)
- ✅ `README.md` (setup instructions)
- ✅ GitHub repo: `https://github.com/OpenClawDani/kilter-training-app`

---

## ✨ Next Steps (After This Discussion)

1. **Daniele approves plan** ← You decide here
2. **CloudCode planning** — Detailed first sprint tasks
3. **Database schema** — Define models + migrations
4. **API specs** — Define endpoints + request/response
5. **Start coding!**

---

**Presentazione preparata da:** Sam  
**Data:** 18/02/2026, 11:45 CET  
**Status:** Ready for 12:00 discussion

---

## 🎬 Demo Mode (If Needed)

If you want to see the current homepage working:
```bash
cd ~/.openclaw/workspace/test-kilter
npm run dev
# Visit http://localhost:3001
```

**What exists now:**
- Homepage with "KILTER UP" branding
- Responsive design (mobile-friendly)
- Dark theme + orange accents

**What's ready to build:**
- All the features above ^

