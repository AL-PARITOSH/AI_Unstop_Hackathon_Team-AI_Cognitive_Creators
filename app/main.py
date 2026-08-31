import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.api.v1.routes import router as v1_router
from app.api.v1.render_views import viewer_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Standalone, modular Visual Explanation Engine for AI Teachers. Generates subject-aware diagrams, flowcharts, graphs, formulas, timelines, code execution traces, and architecture diagrams.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS for external backends & frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure static artifacts directory exists
os.makedirs(settings.STATIC_DIR, exist_ok=True)

# Mount static artifacts for direct file serving
app.mount("/visuals", StaticFiles(directory=settings.STATIC_DIR, html=True), name="visuals_static")

# Include API routes
app.include_router(v1_router, prefix=settings.API_V1_PREFIX)
app.include_router(viewer_router)

@app.get("/", summary="Root Status")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "online",
        "docs_url": "/docs",
        "endpoints": {
            "generate_visual": "POST /generate-visual",
            "select_type": "POST /select-type",
            "visual_types": "GET /visual-types",
            "examples": "GET /examples",
            "health": "GET /health"
        }
    }
