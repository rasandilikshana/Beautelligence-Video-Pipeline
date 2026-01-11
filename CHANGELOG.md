# Changelog

All notable changes to the Beautelligence Video Pipeline project will be documented in this file.

---

## [1.0.0] - 2026-01-12

### 🎉 Initial Release - Full Stack MVP

This is the first production-ready release of the **Beautelligence Video Pipeline**, a complete AI-powered video generation system.

---

### ✨ Features

#### Core Pipeline (CLI)
- **Trend Discovery**: Playwright-based TikTok Creative Center scraper for discovering trending hashtags
- **AI Prompt Generation**: Google Gemini 2.0 Flash integration for creating Veo 3-optimized prompts with brand-safe templates
- **Video Generation**: Google Veo 3 API client for generating 8-second 3D animated character videos (9:16 aspect ratio)
- **Database Layer**: SQLAlchemy async ORM with models for Keywords, Generations, AuditLogs, and DailyQuotas
- **CLI Interface**: Full-featured Typer CLI with commands: `run`, `single`, `test`, `init`, `status`, `config`
- **Docker Support**: Dockerfile and docker-compose.yml for containerized deployment

#### Web Interface (New in v1.0.0)
- **FastAPI Backend**:
  - REST API endpoints: `/api/generate`, `/api/status`, `/api/videos`, `/api/queue`
  - CORS middleware for frontend integration
  - Static file serving for generated videos
  - Background task processing

- **React Frontend**:
  - Modern dark theme (Graphite-inspired aesthetic)
  - Hero landing section with animated entry
  - Generation Studio with prompt input and status tracking
  - Video Gallery with playback support
  - Real-time quota and status dashboard
  - Sample Prompt Template for easy onboarding

- **Branding**:
  - Custom "Beautelligence" logo integration
  - Neon pink/purple color scheme (#ec4899, #a855f7, #d946ef)
  - Inter font family with modern typography

---

### 🛠️ Technical Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.11+, FastAPI, SQLAlchemy (async) |
| Frontend | React 19, Vite, Tailwind CSS 3, Framer Motion |
| AI/ML | Google Gemini 2.0 Flash, Google Veo 3 |
| Database | SQLite (dev) / PostgreSQL (production) |
| Scraping | Playwright |
| CLI | Typer |
| Containerization | Docker, Docker Compose |

---

### 📦 New Files

#### Backend API (`src/api/`)
- `main.py` - FastAPI application entry point
- `routes.py` - API endpoint definitions
- `schemas.py` - Pydantic request/response models

#### Frontend (`frontend/`)
- `src/App.tsx` - Main application layout
- `src/components/Hero.tsx` - Landing section
- `src/components/Generator.tsx` - Prompt input form
- `src/components/Gallery.tsx` - Video display grid
- `src/components/Status.tsx` - Quota dashboard
- `tailwind.config.js` - Custom theme configuration
- `public/branding/` - Logo assets

---

### 🐛 Bug Fixes
- Fixed CORS configuration for cross-origin video playback
- Added `crossOrigin="anonymous"` to video elements for ORB compliance
- Mounted `/data` as StaticFiles for proper media serving
- Resolved Tailwind v4/v3 compatibility issues

---

### 📖 Documentation
- Updated `README.md` with comprehensive project overview
- Added Quick Start guide for backend and frontend
- Documented all completed development phases

---

### 🚀 Getting Started

```bash
# Backend
source venv/bin/activate
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Frontend
cd frontend && npm run dev
```

Access the application at **http://localhost:5173**

---

### Contributors
- Beautelligence AI Team
