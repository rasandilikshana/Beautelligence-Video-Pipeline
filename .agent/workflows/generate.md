---
description: Generate videos with the pipeline
---

# Video Generation Workflow

Use these commands to generate videos.

## Test Mode (No API Keys Required)

// turbo
1. Run mock pipeline:
```bash
python main.py test
```

---

## Single Video Generation

2. Generate for specific keyword:
```bash
python main.py single "strawberry"
```

3. Force generate (skip duplicate check):
```bash
python main.py single "mango" --force
```

4. Mock mode single:
// turbo
```bash
python main.py single "avocado" --mock
```

---

## Batch Generation

5. Run with default quota (3 videos):
```bash
python main.py run
```

6. Specify count:
```bash
python main.py run --videos 5
```

7. Mock batch:
// turbo
```bash
python main.py run --videos 2 --mock
```

---

## Check Results

// turbo
8. View status:
```bash
python main.py status
```

// turbo
9. List generated videos:
```bash
ls -la data/videos/
```

// turbo
10. List prompt logs:
```bash
ls -la data/prompts/
```
