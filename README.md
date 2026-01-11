# Beautelligence Video Pipeline 🎬

An automated video generation pipeline that discovers trending topics and creates engaging short-form videos using Google's **Veo 3 AI** with synchronized audio.

## ✨ Features

- **🔍 Trend Discovery** - Automatically scrapes TikTok Creative Center for trending hashtags
- **🤖 AI Prompt Generation** - Uses Gemini AI to create optimized video prompts
- **🎥 Veo 3 Video Generation** - Generates high-quality videos with audio using Google's Veo 3
- **📊 Database Tracking** - SQLite/PostgreSQL storage for keywords, generations, and quotas
- **🔄 Quota Management** - Daily limits and API call tracking
- **🛡️ Brand Safety** - Filters out inappropriate or risky content
- **📝 Audit Logging** - Complete operation history

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Google API Key with Gemini and Veo 3 access

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd "Veo 3 Vedio Generator and Social Media Publish Workflow"

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your Google API Key
nano .env  # or use any editor
```

### Configuration

Edit `.env` file with your settings:

```env
# Required
GOOGLE_API_KEY=your_google_api_key_here

# Database (SQLite default, or use PostgreSQL)
DATABASE_URL=sqlite+aiosqlite:///data/pipeline.db

# Video Settings
VEO_MODEL=veo-3.0-fast-generate-001
VEO_ASPECT_RATIO=9:16
VEO_DURATION_SECONDS=8
VEO_RESOLUTION=720p

# Daily Limits
DAILY_VIDEO_LIMIT=2
```

### Initialize & Run

```bash
# Initialize database
python main.py init

# Test the pipeline (no API calls)
python main.py test

# Generate video for a specific keyword
python main.py single "dancing strawberry" --force

# Run full pipeline (discover trends + generate)
python main.py run

# Check status
python main.py status
```

## 📖 Commands Reference

| Command | Description |
|---------|-------------|
| `python main.py init` | Initialize database and directories |
| `python main.py test` | Test pipeline with mock data |
| `python main.py single "keyword"` | Generate video for specific keyword |
| `python main.py single "keyword" --force` | Force regenerate even if exists |
| `python main.py single "keyword" --mock` | Test without API calls |
| `python main.py run` | Discover trends and generate videos |
| `python main.py run --mock` | Run with mock services |
| `python main.py status` | Show pipeline and quota status |
| `python main.py config` | Display current configuration |
| `python main.py version` | Show version information |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         CLI (main.py)                        │
├─────────────────────────────────────────────────────────────┤
│                    VideoPipeline Orchestrator                │
├──────────────┬──────────────┬──────────────┬───────────────┤
│   Discover   │    Prompt    │    Video     │   Database    │
│   Service    │   Generator  │   Generator  │  Repositories │
├──────────────┼──────────────┼──────────────┼───────────────┤
│ TikTok CC    │ Gemini AI    │   Veo 3      │   SQLAlchemy  │
│ Scraper      │ (2.0 Flash)  │   API        │   Async       │
└──────────────┴──────────────┴──────────────┴───────────────┘
```

## 📁 Project Structure

```
├── main.py                 # CLI entry point
├── config/
│   ├── settings.py         # Pydantic configuration
│   └── logging.py          # Structured logging setup
├── src/
│   ├── models/
│   │   ├── database.py     # SQLAlchemy async engine
│   │   ├── keyword.py      # Keyword model
│   │   ├── generation.py   # Generation tracking model
│   │   └── audit.py        # Audit log & quota models
│   ├── repositories/
│   │   ├── keyword_repo.py    # Keyword CRUD operations
│   │   ├── generation_repo.py # Generation CRUD operations
│   │   └── quota_repo.py      # Quota management
│   ├── services/
│   │   ├── discover/
│   │   │   ├── tiktok_creative_center.py  # TikTok scraper
│   │   │   └── trend_aggregator.py        # Trend filtering
│   │   ├── prompt/
│   │   │   ├── prompt_templates.py        # Video prompt templates
│   │   │   └── gemini_prompt_generator.py # AI prompt enhancement
│   │   └── video/
│   │       └── veo_client.py              # Veo 3 API client
│   ├── orchestrator/
│   │   └── pipeline.py     # Main workflow orchestration
│   └── utils/
│       ├── retry.py        # Async retry with backoff
│       ├── rate_limiter.py # Token bucket rate limiting
│       └── file_manager.py # File operations
├── data/
│   ├── videos/             # Generated video files
│   ├── prompts/            # Saved prompts
│   └── logs/               # Application logs
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration
├── .env.example            # Environment template
└── .gitignore
```

## 🎬 Veo 3 API Integration

This pipeline uses Google's **Veo 3** video generation model with the following capabilities:

### Supported Models
| Model | Description |
|-------|-------------|
| `veo-3.0-generate-001` | Standard quality, balanced speed |
| `veo-3.0-fast-generate-001` | Faster generation, optimized for throughput |
| `veo-3.1-generate-preview` | Latest preview with advanced features |
| `veo-3.1-fast-generate-preview` | Fast preview version |

### Video Specifications
- **Duration**: 4, 6, or 8 seconds
- **Aspect Ratio**: 9:16 (vertical/TikTok) or 16:9 (horizontal)
- **Resolution**: 720p (1080p for 8s only)
- **Frame Rate**: 24fps
- **Audio**: Automatically generated synchronized audio

### API Usage Pattern
```python
from google import genai
from google.genai import types

client = genai.Client(api_key="YOUR_API_KEY")

# Generate video
operation = client.models.generate_videos(
    model="veo-3.0-fast-generate-001",
    prompt="A cute dancing strawberry character",
    config=types.GenerateVideosConfig(
        aspectRatio="9:16",
        durationSeconds=8,
        numberOfVideos=1,
    ),
)

# Poll for completion
while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation)

# Download and save
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("output.mp4")
```

## 🧠 Prompt Generation

The pipeline uses a two-tier prompt system:

### 1. Template-Based Prompts
Pre-defined templates for cute character animations with:
- Eye styles (googly, anime, cartoon, sparkly)
- Emotions (happy, excited, curious, cheerful)
- Actions (dancing, waving, jumping, spinning)
- Backgrounds (magical forest, candy land, studio)
- Audio moods (upbeat, playful, whimsical)

### 2. AI-Enhanced Prompts
Uses **Gemini 2.0 Flash** to generate creative, detailed prompts:
- Understands trending context
- Creates engaging narratives
- Includes audio/sound effect cues
- Optimized for Veo 3 capabilities

## 📊 Database Schema

### Keywords Table
Stores discovered and manual keywords:
- Status tracking (pending, used, skipped)
- Trending scores
- Expiration dates
- Brand safety metadata

### Generations Table
Tracks all video generation attempts:
- Full prompts and negative prompts
- Video file paths
- Generation status and errors
- Timing and retry counts

### Daily Quotas
Manages API usage limits:
- Videos generated per day
- Gemini API calls
- Veo API calls

### Audit Logs
Complete operation history for debugging and analytics.

## ⚙️ Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `GOOGLE_API_KEY` | Required | Google AI API key |
| `DATABASE_URL` | `sqlite+aiosqlite:///data/pipeline.db` | Database connection |
| `VEO_MODEL` | `veo-3.0-fast-generate-001` | Veo model to use |
| `VEO_ASPECT_RATIO` | `9:16` | Video aspect ratio |
| `VEO_DURATION_SECONDS` | `8` | Video length |
| `VEO_RESOLUTION` | `720p` | Output resolution |
| `DAILY_VIDEO_LIMIT` | `2` | Max videos per day |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Prompt generation model |
| `LOG_LEVEL` | `INFO` | Logging verbosity |

## 🔒 Safety & Filtering

The pipeline includes multiple safety layers:

1. **Brand Safety Filter** - Blocks inappropriate keywords
2. **Negative Prompts** - Excludes unwanted content (violence, horror, etc.)
3. **Veo Safety Filters** - Google's built-in content moderation
4. **SynthID Watermarking** - All videos are watermarked as AI-generated

## 🐛 Troubleshooting

### "No module named 'typer'"
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "403 Permission Denied" on video download
This was fixed in the latest version. The pipeline now uses the official SDK download pattern:
```python
client.files.download(file=video.video)
video.video.save("output.mp4")
```

### "Model not found" error
Ensure you're using a valid model name:
- `veo-3.0-fast-generate-001` ✅
- `veo-3.0-generate-001` ✅

### Database connection issues
For SQLite, ensure the data directory exists:
```bash
python main.py init
```

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `python main.py test`
5. Submit a pull request

---

Built with ❤️ using Google Veo 3 and Gemini AI
