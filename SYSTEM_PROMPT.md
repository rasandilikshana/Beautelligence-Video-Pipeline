# Beautelligence AI Video Pipeline - System Prompt & Architecture

## Executive Summary

A production-ready automated pipeline that discovers trending TikTok topics, generates optimized video prompts via Gemini, creates cute animated character videos using Veo 3, and tracks all operations to ensure keyword deduplication.

---

## System Prompt for AI Agent Orchestrator

```
You are the Beautelligence Video Pipeline Orchestrator, an autonomous agent responsible for managing the daily video generation workflow for the Beautelligence social media brand.

## BRAND IDENTITY
- Channel Theme: Cute 3D animated food/fruit/object characters with expressive faces, vibrant colors, and wholesome scenarios
- Visual Style: High-quality 3D renders similar to Pixar-style characters - soft lighting, glossy textures, anthropomorphic food items with googly eyes and cheerful expressions
- Target Platforms: TikTok (@beautelligence), YouTube (@Beautelligence), Instagram (@beautelligence99), Facebook (beautelligence)
- Content Format: 8-second vertical videos (9:16 aspect ratio) with synchronized audio

## CORE RESPONSIBILITIES

### 1. Trend Discovery
- Query TikTok Creative Center for trending hashtags in the "cute", "satisfying", "animation", "food", "wholesome" niches
- Filter trends for brand alignment (family-friendly, positive sentiment)
- Cross-reference with Google Trends for validation
- Store discovered keywords with timestamp and metadata

### 2. Deduplication Check
- Before processing any keyword, query the PostgreSQL database
- Check if keyword (or semantic equivalent) has been used in past 30 days
- If duplicate found, skip and select next trending topic
- Log skip reason for analytics

### 3. Prompt Generation
- Use Gemini Pro to craft Veo 3-optimized prompts
- Include brand-specific style guidelines in every prompt
- Generate negative prompts to avoid unwanted elements
- Output structured JSON with prompt, negative_prompt, and metadata

### 4. Video Generation
- Call Veo 3 Fast API with generated prompt
- Configure: 9:16 aspect ratio, 720p, 8 seconds, audio enabled
- Implement retry logic with exponential backoff
- Validate output before marking as complete

### 5. State Management
- Record all operations in PostgreSQL
- Update keyword status (pending → processing → complete/failed)
- Store video file references and metadata
- Maintain audit trail for debugging

## DECISION RULES

### Keyword Selection Criteria
- Minimum trending score: 70/100
- Must NOT contain: violence, adult content, controversial topics, political themes
- Preference for: food, animals, objects that can be "cutified"
- Maximum keyword age: 48 hours from first detection

### Prompt Engineering Standards
- Always start with: "A cute 3D animated [object] character with big expressive eyes"
- Include lighting: "soft studio lighting with subtle rim light"
- Include texture: "glossy plastic-like texture with soft shadows"
- Include emotion: specify the character's mood (happy, surprised, excited)
- Include action: what is the character doing
- Include environment: describe the setting briefly
- Audio guidance: "cheerful background music with satisfying sound effects"

### Failure Handling
- API timeout: retry 3 times with 30s, 60s, 120s delays
- Rate limit: pause pipeline for 15 minutes, then resume
- Content filter rejection: log and skip keyword, mark as "filtered"
- Generation failure: retry once with simplified prompt

## OUTPUT FORMAT

Every operation must return structured data:

```json
{
  "operation_id": "uuid",
  "timestamp": "ISO8601",
  "stage": "discover|generate_prompt|generate_video|complete",
  "status": "success|failure|skipped",
  "data": {},
  "error": null
}
```

## RATE LIMITS & QUOTAS
- Daily video quota: 3 videos
- TikTok Creative Center: scrape once per 6 hours
- Gemini API: 60 RPM (free tier)
- Veo 3 Fast: respect daily generation limits

## ETHICAL GUIDELINES
- Never generate content depicting real people
- Avoid cultural stereotypes
- Maintain G-rated content suitable for all ages
- Respect copyright - no branded characters or logos
```

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                        BEAUTELLIGENCE VIDEO PIPELINE                         │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌────────────────┐                                                          │
│  │   SCHEDULER    │  (Cron: 0 6 * * *)                                       │
│  │   main.py      │                                                          │
│  └───────┬────────┘                                                          │
│          │                                                                   │
│          ▼                                                                   │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                         ORCHESTRATOR                                │     │
│  │                      (orchestrator.py)                              │     │
│  │  - Manages pipeline state                                          │     │
│  │  - Coordinates all stages                                          │     │
│  │  - Handles errors & retries                                        │     │
│  └──────────────────────────┬─────────────────────────────────────────┘     │
│                             │                                                │
│     ┌───────────────────────┼───────────────────────────┐                   │
│     │                       │                           │                   │
│     ▼                       ▼                           ▼                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐          │
│  │   DISCOVER   │    │   PROMPT     │    │      GENERATE        │          │
│  │   SERVICE    │    │   SERVICE    │    │      SERVICE         │          │
│  │              │    │              │    │                      │          │
│  │ - TikTok CC  │    │ - Gemini API │    │ - Veo 3 Fast API     │          │
│  │ - Scraper    │    │ - Template   │    │ - File management    │          │
│  │ - G. Trends  │    │   Engine     │    │ - Validation         │          │
│  └──────┬───────┘    └──────┬───────┘    └──────────┬───────────┘          │
│         │                   │                       │                       │
│         └───────────────────┴───────────────────────┘                       │
│                             │                                                │
│                             ▼                                                │
│  ┌────────────────────────────────────────────────────────────────────┐     │
│  │                      DATA LAYER                                     │     │
│  │                                                                     │     │
│  │  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐     │     │
│  │  │   PostgreSQL    │  │   File Store    │  │    Redis        │     │     │
│  │  │                 │  │                 │  │   (Optional)    │     │     │
│  │  │ - keywords      │  │ - /videos/      │  │ - Rate limits   │     │     │
│  │  │ - generations   │  │ - /prompts/     │  │ - Cache         │     │     │
│  │  │ - audit_logs    │  │ - /logs/        │  │                 │     │     │
│  │  └─────────────────┘  └─────────────────┘  └─────────────────┘     │     │
│  └────────────────────────────────────────────────────────────────────┘     │
│                                                                              │
│  [PHASE 2: Social Media Publisher - TikTok/YT/IG/FB APIs]                   │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Database Schema

```sql
-- Core tables for the video pipeline

-- Keywords discovered from trending sources
CREATE TABLE keywords (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword VARCHAR(255) NOT NULL,
    keyword_normalized VARCHAR(255) NOT NULL,  -- lowercase, stripped
    source VARCHAR(50) NOT NULL,  -- 'tiktok_cc', 'google_trends'
    trending_score INTEGER,
    discovered_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, used, skipped, expired
    skip_reason VARCHAR(255),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    CONSTRAINT unique_keyword_30days UNIQUE (keyword_normalized, (DATE_TRUNC('month', discovered_at)))
);

CREATE INDEX idx_keywords_status ON keywords(status);
CREATE INDEX idx_keywords_discovered ON keywords(discovered_at DESC);
CREATE INDEX idx_keywords_normalized ON keywords(keyword_normalized);

-- Video generation records
CREATE TABLE generations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword_id UUID REFERENCES keywords(id),
    prompt TEXT NOT NULL,
    negative_prompt TEXT,
    prompt_metadata JSONB,
    
    -- Veo 3 specifics
    veo_model VARCHAR(50) DEFAULT 'veo-3.0-fast-generate-001',
    aspect_ratio VARCHAR(10) DEFAULT '9:16',
    resolution VARCHAR(10) DEFAULT '720p',
    duration_seconds INTEGER DEFAULT 8,
    
    -- Output
    video_file_path VARCHAR(500),
    video_url VARCHAR(500),
    file_size_bytes BIGINT,
    
    -- Status tracking
    status VARCHAR(20) DEFAULT 'pending',  -- pending, generating, complete, failed
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_generations_status ON generations(status);
CREATE INDEX idx_generations_keyword ON generations(keyword_id);
CREATE INDEX idx_generations_created ON generations(created_at DESC);

-- Audit log for debugging and analytics
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operation VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),  -- 'keyword', 'generation', 'api_call'
    entity_id UUID,
    action VARCHAR(50) NOT NULL,  -- 'create', 'update', 'api_call', 'error'
    details JSONB,
    error_details JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_created ON audit_logs(created_at DESC);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

-- Daily quotas tracking
CREATE TABLE daily_quotas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quota_date DATE NOT NULL UNIQUE,
    videos_generated INTEGER DEFAULT 0,
    videos_limit INTEGER DEFAULT 3,
    api_calls_gemini INTEGER DEFAULT 0,
    api_calls_veo INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE UNIQUE INDEX idx_quotas_date ON daily_quotas(quota_date);

-- Publishing queue (Phase 2)
CREATE TABLE publishing_queue (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    generation_id UUID REFERENCES generations(id),
    platform VARCHAR(20) NOT NULL,  -- 'tiktok', 'youtube', 'instagram', 'facebook'
    scheduled_at TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE,
    status VARCHAR(20) DEFAULT 'pending',  -- pending, scheduled, published, failed
    platform_post_id VARCHAR(255),
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_publishing_status ON publishing_queue(status, scheduled_at);
```

---

## Project Structure

```
beautelligence-video-pipeline/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── .env                          # (gitignored)
├── docker-compose.yml
├── Dockerfile
│
├── config/
│   ├── __init__.py
│   ├── settings.py               # Pydantic settings management
│   └── logging.py                # Structured logging config
│
├── src/
│   ├── __init__.py
│   │
│   ├── orchestrator/
│   │   ├── __init__.py
│   │   ├── pipeline.py           # Main pipeline orchestration
│   │   └── scheduler.py          # Cron job management
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── discover/
│   │   │   ├── __init__.py
│   │   │   ├── tiktok_creative_center.py
│   │   │   ├── google_trends.py
│   │   │   └── trend_aggregator.py
│   │   │
│   │   ├── prompt/
│   │   │   ├── __init__.py
│   │   │   ├── gemini_client.py
│   │   │   ├── prompt_templates.py
│   │   │   └── prompt_generator.py
│   │   │
│   │   └── video/
│   │       ├── __init__.py
│   │       ├── veo_client.py
│   │       └── video_validator.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── keyword.py            # SQLAlchemy models
│   │   ├── generation.py
│   │   └── audit.py
│   │
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── keyword_repo.py
│   │   ├── generation_repo.py
│   │   └── quota_repo.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── retry.py              # Retry decorators
│       ├── rate_limiter.py
│       └── file_manager.py
│
├── scripts/
│   ├── init_db.py                # Database initialization
│   ├── run_pipeline.py           # Manual pipeline trigger
│   └── backfill_keywords.py      # Utility scripts
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_discover.py
│   ├── test_prompt.py
│   └── test_video.py
│
└── data/
    ├── videos/                   # Generated videos
    ├── prompts/                  # Prompt logs
    └── logs/                     # Application logs
```

---

## Environment Configuration

```bash
# .env.example

# ===================
# APPLICATION
# ===================
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=INFO

# ===================
# DATABASE
# ===================
DATABASE_URL=postgresql://beautelligence:password@localhost:5432/beautelligence_pipeline
DATABASE_POOL_SIZE=5

# ===================
# GOOGLE AI / GEMINI
# ===================
GOOGLE_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash

# ===================
# VEO 3 VIDEO GENERATION
# ===================
# Option 1: Direct Google API (requires billing)
VEO_MODEL=veo-3.0-fast-generate-001
VEO_RESOLUTION=720p
VEO_ASPECT_RATIO=9:16
VEO_DURATION_SECONDS=8

# Option 2: Third-party API (Kie.ai - more affordable)
# KIE_API_KEY=your_kie_api_key_here
# KIE_API_URL=https://api.kie.ai/v1

# ===================
# TIKTOK SCRAPING
# ===================
# TikTok Creative Center doesn't require auth for public data
TIKTOK_CC_BASE_URL=https://ads.tiktok.com/business/creativecenter
TIKTOK_REGION=US
TIKTOK_SCRAPE_INTERVAL_HOURS=6

# ===================
# GOOGLE TRENDS (FALLBACK)
# ===================
GOOGLE_TRENDS_REGION=US
GOOGLE_TRENDS_CATEGORY=0

# ===================
# RATE LIMITS
# ===================
DAILY_VIDEO_LIMIT=3
GEMINI_RPM_LIMIT=60
VEO_DAILY_LIMIT=10

# ===================
# FILE STORAGE
# ===================
VIDEO_OUTPUT_DIR=./data/videos
PROMPT_LOG_DIR=./data/prompts
LOG_DIR=./data/logs

# ===================
# OPTIONAL: REDIS CACHE
# ===================
# REDIS_URL=redis://localhost:6379/0
```

---

## Implementation Roadmap

### Phase 1: Core Pipeline (Week 1-2)
1. **Day 1-2**: Project setup, database schema, Docker configuration
2. **Day 3-4**: TikTok Creative Center scraper with Playwright
3. **Day 5-6**: Gemini prompt generation service
4. **Day 7-8**: Veo 3 API integration
5. **Day 9-10**: Orchestrator and scheduler
6. **Day 11-12**: Testing, error handling, logging
7. **Day 13-14**: Documentation, deployment scripts

### Phase 2: Enhancements (Week 3-4)
1. Keyword semantic similarity check (avoid near-duplicates)
2. A/B testing different prompt styles
3. Video quality validation
4. Performance monitoring dashboard

### Phase 3: Auto-Publishing (Week 5-6)
1. TikTok API integration
2. YouTube Shorts upload
3. Instagram Reels publishing
4. Facebook video posting
5. Scheduling and analytics

---

## Cost Analysis

### Gemini API (Prompt Generation)
- **Model**: gemini-2.0-flash (free tier)
- **Usage**: ~10 calls/day for prompt generation
- **Cost**: $0 (within free tier limits)

### Veo 3 API (Video Generation)
| Option | Per Video (8s) | Daily (3 videos) | Monthly |
|--------|---------------|------------------|---------|
| Google AI Pro | Included | Included | $19.99 |
| Vertex AI (Fast) | $1.20 | $3.60 | ~$108 |
| Kie.ai (Fast) | $0.40 | $1.20 | ~$36 |

**Recommendation**: Start with Google AI Pro at $19.99/month - includes ~90 Veo 3 Fast videos/month (3/day).

### Infrastructure
- **Dedicated Server**: Your existing setup
- **PostgreSQL**: Self-hosted
- **Storage**: ~500MB/month for videos

**Total Estimated Monthly Cost**: $20-40

---

## Trending Source Strategy

### Primary: TikTok Creative Center
```
URL: https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/en
Data Available:
- Trending hashtags by country
- Trending songs
- Trending creators
- Trending videos

Scraping Method: Playwright (headless browser)
Update Frequency: Every 6 hours
```

### Fallback: Google Trends
```python
# Using pytrends library
from pytrends.request import TrendReq

pytrends = TrendReq(hl='en-US', tz=360)
pytrends.build_payload(kw_list=['cute animation', 'satisfying video'])
trending = pytrends.trending_searches(pn='united_states')
```

### Keyword Filtering Pipeline
```
Raw Keywords → Brand Filter → Sentiment Check → Duplicate Check → Queue
     ↓              ↓              ↓               ↓
  TikTok CC    Family-safe    Positive only   30-day window
```

---

## Prompt Template System

```python
# Base template for Beautelligence brand
BEAUTELLIGENCE_PROMPT_TEMPLATE = """
A cute 3D animated {object} character with big expressive {eye_style} eyes and a {emotion} expression.

The character is {action} in a {environment}.

Visual Style:
- Soft studio lighting with subtle rim light
- Glossy plastic-like texture with soft shadows
- Vibrant {color_palette} color palette
- High-quality 3D render, Pixar-style animation quality

Camera: {camera_movement}
Duration: 8 seconds
Audio: {audio_description}
"""

# Example filled template
example_prompt = """
A cute 3D animated papaya character with big expressive googly eyes and a surprised expression.

The character is dancing excitedly while discovering it has tiny arms in a colorful tropical kitchen.

Visual Style:
- Soft studio lighting with subtle rim light
- Glossy plastic-like texture with soft shadows
- Vibrant orange, yellow, and green color palette
- High-quality 3D render, Pixar-style animation quality

Camera: slow zoom in with gentle rotation
Duration: 8 seconds
Audio: upbeat cheerful music with satisfying pop sound effects
"""

# Negative prompt (things to avoid)
NEGATIVE_PROMPT = """
realistic human faces, scary elements, dark themes, violence, 
text overlays, watermarks, low quality, blurry, distorted faces,
inappropriate content, branded logos, copyrighted characters
"""
```

---

## Key Implementation Notes

### 1. Deduplication Logic
```python
async def is_keyword_duplicate(keyword: str, days: int = 30) -> bool:
    """
    Check if keyword (or semantic equivalent) was used recently.
    Uses normalized form + optional embedding similarity.
    """
    normalized = normalize_keyword(keyword)
    
    # Exact match check
    existing = await keyword_repo.find_by_normalized(
        normalized, 
        since=datetime.now() - timedelta(days=days)
    )
    if existing:
        return True
    
    # Optional: Semantic similarity check using embeddings
    # similar = await check_semantic_similarity(keyword, threshold=0.85)
    # return similar is not None
    
    return False
```

### 2. Retry Pattern
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=30, max=120),
    retry=retry_if_exception_type(APIError)
)
async def generate_video(prompt: str, config: VeoConfig) -> VideoResult:
    """Generate video with automatic retry on transient failures."""
    pass
```

### 3. Rate Limiting
```python
class RateLimiter:
    def __init__(self, calls_per_minute: int):
        self.calls_per_minute = calls_per_minute
        self.calls = []
    
    async def acquire(self):
        now = time.time()
        self.calls = [t for t in self.calls if now - t < 60]
        if len(self.calls) >= self.calls_per_minute:
            sleep_time = 60 - (now - self.calls[0])
            await asyncio.sleep(sleep_time)
        self.calls.append(time.time())
```

---

## Next Steps

1. **Review this document** and confirm the architecture aligns with your vision
2. **Set up Google Cloud project** with billing for Veo 3 API access
3. **Get Gemini API key** from Google AI Studio
4. **Provision PostgreSQL** on your dedicated server
5. **Begin Phase 1 implementation** starting with the database schema

Would you like me to proceed with generating the actual implementation code for any specific component?
