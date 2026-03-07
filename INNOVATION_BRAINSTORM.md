# 💡 Innovation Brainstorm - Kilter Up Unique Features

**Sessione:** 18 Febbraio 2026, 10:00-11:30 CET  
**Scope:** Differenziali competitivi vs Climbology/Climbdex

---

## 🎯 Problem Statement

**Status Quo:**
- Climbdex: Ottimo search engine, ma statico (solo lookup database)
- Climbology: AI beta design, ma complesso da usare (Django setup)
- Kilter App ufficiale: Buono per climb, non per training planning

**Gap:** Non esiste un'app che dica "Tu sei V5, questa settimana fai QUESTO programma" con circuiti generati AI

---

## ✨ Core Innovations

### 1. **"CircuitDetect" - Video Recognition Engine**
**Problema:** Climber salisce un circuito carino, vuole ricordarlo → Prende video, viene dimenticato

**Soluzione:**
- Upload video 30sec → AI riconosce hold pattern
- Match automatico con BoardLib circuits (o crea "Unknown circuit")
- Save automatico nella library personale
- Share link: "Prova questo circuito!" → Amici lo vedono nel loro app

**Innovazione:**
- Unique per climbing apps (first-mover advantage)
- Friction bassa: 1 tap per salvare circuiti
- Feedback loop: più video = migliore AI

**Tech:** Gemini Vision + hold detection ML

---

### 2. **"SmartTrainer" - Adaptive Weekly Plans**
**Problema:** Anche se conosco i miei circuiti favoriti, non so come allenarmi bene

**Soluzione:**
- Input: Tuo skill level (V-grade), muscoli deboli, ore disponibili/week
- Output: Piano settimanale personalizzato
  ```
  Lunedì: Power Day
  - 3x V7 max attempts
  - 3x V5 1-minute holds
  
  Mercoledì: Endurance
  - 4x circuits (moderate difficulty)
  - 8min total climb time
  
  Venerdì: Weakness Day
  - Tutti i problemi con "jug" scarsi
  - Focus: grip strength
  ```
- Week-by-week adaptation: "Hai climato molto bene, upgraded i V5s a V6 prossima settimana"

**Innovazione:**
- Clustering degli ascensioni → identifica weakness
- Forecasting: "In 8 settimane sarai V6 se mantieni questo ritmo"
- Gamification: Streak counter, weekly achievements

**Tech:** LightGBM clustering + time-series prediction

---

### 3. **"FormGuide" - Real-time Biomechanics Feedback**
**Problema:** "Fai male quella mossa ma non sai come" - bisogna video sé stessi e analizz

arlo

**Soluzione (Fase avanzata):**
- Webcam during climb → skeleton tracking in real-time
- AI feedback: "Hip closer to wall!", "Less arm!", "Weight feet"
- Post-climb: Video analysis + segmented hints per hold
- Comparison: Vedi tua forma vs expert climber su stesso circuito

**Why it's unique:**
- Belay AI fa simile, ma non integrato con training
- Kilter Up lo integra: Form feedback → suggerisce grip exercises

**Tech:** MediaPipe pose detection + Gemini Vision for coaching hints

---

### 4. **"CircuitRemix" - Social Circuit Building**
**Problema:** Circuiti esistenti sono fixed; climbers vorrebbero customizzare

**Soluzione:**
- Climber crea: "V5 Power" circuit template
- Comunità remixxa: Cambia 2 holds, lo chiama "V5 Power Extended"
- Versioning: Originale + 10 varianti, tutti trackati
- Leaderboard: "Hardest remix of this week's circuit"

**Innovazione:**
- Crowdsourced circuit improvement
- Social engagement (likes, comments)
- Automatically identifies "best variants" by ascent success

**Tech:** Graph database (Neo4j) + versioning system

---

### 5. **"GymMatch" - Kilter Board Specific Training**
**Problema:** Climber sa che è V6, ma non sa quali circuiti del suo gym lo faranno progredire

**Soluzione:**
- Input: Scegli tuo gym con Kilterboard (nearby location)
- App mostra: "Hot circuits questa settimana" (most attempted by your level)
- Suggerisce: "Top 3 circuiti for V6→V7 progression"
- Community stats: "Questo circuito ha 60% ascensione rate a V6, sei tra i top10"

**Innovazione:**
- Location-based training
- Difficulty calibration per gym (alcuni boards sono più facili)
- Social proof: "800 persone hanno escalato questo; average rating: 4.2/5"

**Tech:** Geolocation + aggregated BoardLib data

---

## 🔄 Cross-Feature Synergies

### Loop: Upload → Detect → Train → Improve
```
1. Climber uploads circuito video
2. AI riconosce → salva in library
3. SmartTrainer suggerisce di farla 2x/week
4. Climber trackka ascensioni
5. FormGuide dà feedback
6. Nel mese: Circuito diventa "soft" → upgraded to V6 circuits
7. Climber condivide success → CircuitRemix community ride lo
```

### Loop: Weakness Detection → Training → Strength Gain
```
1. Analysis: "Tuoi V5s hanno 70% jug holds, ma solo 5% sloper success"
2. SmartTrainer: "Questa settimana: all sloper circuits"
3. 4 settimane dopo: "Sloper success rate +40%"
4. Notification: "You unlocked 'Sloper Master' badge!"
```

---

## 🎮 Gamification Elements (Non-intrusive)

1. **Badges:**
   - 🏔️ "First Video" - Upload primo circuito
   - 📈 "Grade Jump" - Escalate a grade superiore
   - 🔧 "Form Perfectionist" - 10 perfect climbs con FormGuide tips
   - 🤝 "Remixer" - Crea 5 varianti di circuiti

2. **Streaks:**
   - "Training Consistency: 12 days" with calendar view
   - "Gym Streak: 8 consecutive weeks"

3. **Leaderboards:**
   - Weekly: "Most videos analyzed"
   - Monthly: "Most circuiti climbed"
   - Lifetime: "Grade progression speed"

4. **Challenges:**
   - "V5 Challenge": Climb 10 different V5s in a week
   - "Weakness Month": Upgrade worst hold type by 1 grade

---

## 🚀 Feature Differentiation Matrix

| Feature | Kilter Up | Climbdex | Climbology | Belay AI |
|---------|-----------|----------|-----------|----------|
| Video Recognition | ✅ AI | ❌ | ❌ | ❌ |
| Circuit Generation | ✅ AI-powered | ❌ | ✅ Basic | ❌ |
| Training Plans | ✅ Adaptive | ❌ | ❌ | ❌ |
| Real-time Form Feedback | ✅ Future | ❌ | ❌ | ✅ Limited |
| Social/Remix | ✅ | ❌ | ❌ | ❌ |
| Gym-specific Calibration | ✅ | ✅ | ❌ | ❌ |
| Performance Prediction | ✅ | ❌ | ❌ | ❌ |

---

## 💰 Monetization Ideas (Post-MVP)

1. **Freemium:**
   - Free: 10 video uploads/month, basic training plans
   - Premium ($4.99/month): Unlimited uploads, FormGuide, advanced analytics

2. **Coach Tools:**
   - Gym coaches ($9.99/month): Manage club members, track classes

3. **Data API:**
   - Third-party developers: Access anonymized training data for coaching app

4. **Partnerships:**
   - Kilter Board official: In-app circuit export → board directly
   - Climbing brands: Recommend gear ("You grip problem, try Tenaya X")

---

## 🎬 Demo Script (for presentation @ 12:00)

**Scenario 1: Video Upload**
- "Ecco un video mio che arrampico un circuito cool"
- Upload → AI analysis: "Detected as V6 Power Circuit variant"
- Mostra: Holds overlay sul video + Predicted difficulty
- Option: Salva, condividi, aggiugi al training plan

**Scenario 2: SmartTrainer in Action**
- Dashboard mostra: "This week: 3 V5 ascensioni, 0 V6"
- Piano suggerito:
  ```
  MON: 3x V6 power circuits
  WED: V5 endurance loops
  FRI: Focus on your weak spots
  ```
- Climber approva/customizza → Aggiunte al calendar

**Scenario 3: Weekly Progress**
- "This month: 5 new grades reached"
- Visualizzazione: Grade distribution graph, muscoli usati,  improvements
- Forecast: "At this pace, V7 in 6 weeks"

---

## ⚠️ Competitive Advantages (Why This Wins)

1. **First-mover:** Nessuno ha video recognition per climbing yet
2. **Integrated:** Video + Training + Form in 1 app (competitors sono separati)
3. **Community:** Social remix features + leaderboards (engagement!)
4. **Data-driven:** Real forecasting, not just logging
5. **Friction-low:** 1 tap to save any circuito (instant gratification)

---

## 🎯 MVP Scope (What We Actually Build Week 1-4)

**IN:**
- ✅ Homepage (done)
- ✅ Video upload + frame extraction
- ✅ Gemini Vision for hold detection
- ✅ Match con BoardLib circuits
- ✅ Circuit gallery + viewer
- ✅ Basic training log
- ✅ Weekly plan generator (simple version)

**OUT (Post-MVP):**
- ❌ FormGuide (skeleton tracking)
- ❌ CircuitRemix (social)
- ❌ GymMatch (geolocation)
- ❌ Advanced analytics
- ❌ Mobile app

---

## 📝 Next Steps

1. **Discussione:** Daniele approva direction?
2. **Refinement:** CloudCode planning discussion
3. **Sprint Planning:** Definisci task per Week 1
4. **Tech Setup:** DB schema, API endpoints
5. **Development:** Start Week 1 sprint

---

**Documento creato da:** Sam  
**Data:** 18/02/2026, 11:15 CET  
**Status:** Ready for discussion

