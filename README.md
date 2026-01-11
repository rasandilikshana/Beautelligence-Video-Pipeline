# Beautelligence Video Pipeline

## Project Overview
**Beautelligence** is an automated AI video generation pipeline designed to create cute, 3D animated character videos for social media. It leverages advanced AI technologies to discover trending topics, generate creative prompts, and produce high-quality videos optimized for engagement.

### Key Features
*   **Trend Discovery**: Automatically scrapes TikTok Creative Center for trending hashtags and topics.
*   **AI-Powered Content**: Uses **Google Gemini 2.0 Flash** to generate engaging, Veo 3-optimized prompts.
*   **Video Generation**: Integrated with **Google Veo 3** for generating stunning 8-second 3D animated videos.
*   **Web Interface**: A modern, dark-themed React frontend with a "Graphite" inspired aesthetic for easy management.
*   **Robust Backend**: FastAPI-based REST API handling queues, quotas, and generation tasks.

---

## 🚀 Quick Start

### 1. Prerequisites
*   Python 3.11+
*   Node.js 18+
*   Google API Key (with Gemini and Veo 3 access)

### 2. Backend Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python main.py init

# Start the API server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access the application at **http://localhost:5173**.

---

## 📋 Project Status & Task Breakdown

### Phase 1: Project Foundation ✅
*   [x] **Project Setup**: `requirements.txt`, `pyproject.toml`, `.env` template, `.gitignore`.
*   [x] **Configuration**: Pydantic settings management, structured logging.

### Phase 2: Database Layer ✅
*   [x] **Models**: SQLAlchemy async engines, models for Keywords, Generations, and Audit logs.
*   [x] **Repositories**: Data access layers for all models.

### Phase 3: Core Services ✅
*   [x] **Discover Service**: Playwright-based TikTok trend scraper.
*   [x] **Prompt Service**: Gemini AI prompt generator with brand-safe templates.
*   [x] **Video Service**: Google Veo 3 client for video generation.

### Phase 4: Utilities & Orchestration ✅
*   [x] **Utilities**: Retry decorators, rate limiting, file management.
*   [x] **Orchestrator**: Main pipeline logic connecting all services.

### Phase 5: CLI & Docker ✅
*   [x] **CLI**: Typer-based command line interface (`main.py`).
*   [x] **Docker**: Dockerfile and Compose setup for containerization.

### Phase 6: Testing ✅
*   [x] **Unit Tests**: Basic test coverage for discovery and prompt services.

### Phase 7: Web API Backend (FastAPI) ✅
*   [x] **API Core**: FastAPI app structure, schemas, and routes.
*   [x] **Integration**: Connected pipeline to REST endpoints (`/generate`, `/status`, `/videos`).

### Phase 8: Web Frontend (React + Tailwind) ✅
*   [x] **Setup**: Vite + React + TypeScript + Tailwind CSS.
*   [x] **UI Implementation**:
    *   **Hero Section**: Attractive landing page.
    *   **Generation Studio**: Form for creating videos.
    *   **Gallery**: Grid view of generated content.
    *   **Status Dashboard**: Real-time quota and system monitoring.

### Phase 9: UI Polish & Branding ✅
*   [x] **Custom Branding**: Added "Beautelligence" logo and neon pink/purple aesthetic.
*   [x] **UX Enhancements**: Improved visibility, added **Sample Prompt Tile** for easy testing.

---

## 🛠️ CLI Usage
You can also run the pipeline directly via the command line:

```bash
# Run the full daily pipeline
python main.py run

# Generate a video for a specific keyword
python main.py single "cute strawberry"

# Check system status
python main.py status
```
