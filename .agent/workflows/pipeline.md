---
description: Run pipeline commands for video generation
---

# Beautelligence Pipeline CLI Workflow

Use these commands to operate the video generation pipeline.

## Setup (First Time Only)

// turbo
1. Create virtual environment:
```bash
python -m venv venv
```

// turbo
2. Activate virtual environment:
```bash
source venv/bin/activate
```

// turbo
3. Install dependencies:
```bash
pip install -r requirements.txt
```

// turbo
4. Install Playwright browser:
```bash
playwright install chromium
```

## Database Setup

// turbo
5. Start PostgreSQL (Docker):
```bash
docker-compose up -d postgres
```

// turbo
6. Initialize database:
```bash
python main.py init
```

---

## Daily Operations

### Test Pipeline (Mock Mode - No API Calls)
// turbo
```bash
python main.py test
```

### Run Full Pipeline
```bash
python main.py run
```

### Run With Specific Video Count
```bash
python main.py run --videos 3
```

### Generate Single Keyword
```bash
python main.py single "strawberry"
```

### Force Generate (Skip Duplicate Check)
```bash
python main.py single "mango" --force
```

---

## Monitoring

### Check Status
// turbo
```bash
python main.py status
```

### View Configuration
// turbo
```bash
python main.py config
```

### View Version
// turbo
```bash
python main.py version
```

### View Logs
// turbo
```bash
tail -f data/logs/*.log
```

---

## Docker Commands

### Start All Services
```bash
docker-compose up -d
```

### Run Pipeline Once
```bash
docker-compose run --rm runner
```

### Development Mode
```bash
docker-compose --profile development up dev
```

### View Docker Logs
// turbo
```bash
docker-compose logs -f runner
```

### Stop All Services
```bash
docker-compose down
```

---

## Development

### Run Tests
// turbo
```bash
pytest tests/ -v
```

### Format Code
// turbo
```bash
black .
```

### Lint Code
// turbo
```bash
ruff check .
```
