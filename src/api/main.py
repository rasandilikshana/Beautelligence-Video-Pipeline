from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.api.routes import router
from src.models.database import init_db
from config.settings import settings
from config.logging import setup_logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging(settings.log_level, settings.log_dir)
    await init_db()
    settings.ensure_directories()
    yield
    # Shutdown (if needed)

app = FastAPI(
    title="Beautelligence API",
    description="Video Generation Pipeline API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",
    "*", # For development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles

# ... existing imports ...

app.include_router(router, prefix="/api")

# Mount data/videos directory for static access
app.mount("/data", StaticFiles(directory="data"), name="data")

@app.get("/")
def read_root():
    return {"message": "Beautelligence API is running 🚀"}
