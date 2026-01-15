from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from contextlib import asynccontextmanager
from pathlib import Path

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

# Include API routes
app.include_router(router, prefix="/api")

# Mount data/videos directory for static access
app.mount("/data", StaticFiles(directory="data"), name="data")

# Frontend static files - serve built frontend
FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend" / "dist"

if FRONTEND_DIR.exists():
    # Serve static assets (JS, CSS, images)
    app.mount("/assets", StaticFiles(directory=str(FRONTEND_DIR / "assets")), name="assets")
    
    # Serve branding assets (logo, etc.)
    branding_dir = FRONTEND_DIR / "branding"
    if branding_dir.exists():
        app.mount("/branding", StaticFiles(directory=str(branding_dir)), name="branding")
    
    # Serve index.html for all non-API routes (SPA routing)
    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        """Serve frontend for all non-API routes."""
        # Don't serve frontend for API or data routes
        if full_path.startswith("api/") or full_path.startswith("data/"):
            return {"error": "Not found"}
        
        # Serve index.html for SPA routing
        index_file = FRONTEND_DIR / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return {"error": "Frontend not built. Run 'npm run build' in frontend/"}
else:
    @app.get("/")
    def read_root():
        return {"message": "Beautelligence API is running 🚀. Frontend not built."}

