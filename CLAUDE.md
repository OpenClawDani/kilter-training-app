# 🧗 Claude Code Guidelines - Kilter Training App

## Project Overview
**Kilter Training App** - AI-powered circuit generator and training planner for Kilterboard (AI+climbing)

**Primary Tech Stack:**
- Frontend: Next.js + TypeScript
- Backend: Python FastAPI
- AI: Gemini Vision API + BoardLib API integration
- Database: TBD (will be defined)

## Core Rules for Claude Development

### 📋 Code Standards
- **Language**: English for code, Italian for comments when needed
- **Style**: Follow PEP 8 (Python), ESLint (JavaScript/TypeScript)
- **No secrets in code**: Use environment variables for API keys, database credentials
- **Type safety**: Always use TypeScript types, Python type hints

### ✅ ALWAYS Do This
1. **Write tests for every feature** - Unit tests + integration tests
2. **Test locally before push** - Run test suite, verify no errors/warnings
3. **Commit with clear messages**:
   - Format: `feat: short description` or `fix: bug description`
   - Example: `feat: add circuit generation from video analysis`
4. **Push after each working feature** - Small, atomic commits
5. **Document complex logic** - Docstrings for functions, README updates

### ❌ NEVER Do This
1. Commit broken code (tests must pass)
2. Push credentials, API keys, or .env files
3. Change migrations/database schema without discussion
4. Ignore type errors or linting warnings
5. Push without testing locally

### 🏗️ Project Structure
```
kilter-training-app/
├── src/
│   ├── api/          # FastAPI endpoints
│   ├── models/       # Data models
│   ├── services/     # Business logic
│   └── utils/        # Helper functions
├── frontend/         # Next.js application
├── tests/           # Test suite
├── docs/            # Documentation
└── CLAUDE.md        # This file
```

### 🧪 Testing Requirements
- **Backend**: pytest with >80% coverage
- **Frontend**: Jest + React Testing Library
- **Run tests before push**: `pytest` or `npm test`

### 📝 Documentation
- Update README.md for major changes
- Add docstrings to new functions
- Comment complex algorithms
- Document API endpoints in `docs/API.md`

### 🔄 Development Flow
1. **Receive task** → Understand scope + acceptance criteria
2. **Plan** → Identify files to change, dependencies
3. **Code** → Implement with tests
4. **Verify** → Run full test suite
5. **Commit** → Clear message, logical chunks
6. **Push** → `git push origin main` with verification output

### 🎯 Acceptance Criteria Template
When starting work, confirm:
- [ ] Task scope is clear
- [ ] Tests define expected behavior
- [ ] Code changes are minimal/focused
- [ ] All tests pass locally
- [ ] Commit messages are clear
- [ ] No console warnings/errors

### 🛠️ Useful Commands
```bash
# Testing
pytest                    # Run all tests
pytest -v               # Verbose output
pytest --cov           # Coverage report

npm test               # Frontend tests
npm run lint          # Check TypeScript/ESLint

# Git workflow
git status            # Check changes
git diff             # Review changes
git add .            # Stage changes
git commit -m "feat: description"
git push origin main

# Local verification
npm run build        # Build frontend
npm run dev         # Start dev server
```

---

**Version**: 1.0  
**Last Updated**: 2026-02-17  
**Owner**: Daniele Somensi + Sam (Claude Agent)

Questions? Ask before starting the task! 🎯
