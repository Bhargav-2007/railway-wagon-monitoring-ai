from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time

from app.database import engine, Base
from app.api.v1 import frames, health, analytics

# Create database tables
Base.metadata.create_all(bind=engine)

# Track startup time
start_time = time.time()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    print("🚀 Starting Railway Monitoring API...")
    print("✓ Database initialized")
    print("✓ API routes registered")
    yield
    print("👋 Shutting down...")

# Initialize FastAPI app
app = FastAPI(
    title="Railway Wagon Monitoring API",
    description="AI-powered railway wagon monitoring with motion blur detection",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(frames.router, prefix="/api/v1", tags=["frames"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

# Try to include streaming router
try:
    from app.api.v1 import stream
    app.include_router(stream.router, prefix="/api/v1/stream", tags=["streaming"])
    print("✓ Streaming API registered")
except Exception as e:
    print(f"⚠ Streaming API not available: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Railway Wagon Monitoring API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health/"
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    uptime = time.time() - start_time
    return {
        "status": "running",
        "uptime_seconds": uptime,
        "endpoints": {
            "health": "/api/v1/health/",
            "frames": "/api/v1/frames/",
            "analytics": "/api/v1/analytics/summary",
            "streaming": "/api/v1/stream/cameras"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
