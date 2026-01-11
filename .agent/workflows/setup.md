---
description: Quick setup for the video pipeline
---

# Quick Setup Workflow

// turbo-all

Run these commands in order to set up the pipeline from scratch.

## 1. Create Virtual Environment
```bash
python -m venv venv
```

## 2. Activate Environment
```bash
source venv/bin/activate
```

## 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## 4. Copy Environment File
```bash
cp .env.example .env
```

## 5. Start PostgreSQL
```bash
docker-compose up -d postgres
```

## 6. Initialize Database
```bash
python main.py init
```

## 7. Test Pipeline (Mock Mode)
```bash
python main.py test
```

## Done!
The pipeline is ready. Edit `.env` to add your `GOOGLE_API_KEY` for real video generation.
