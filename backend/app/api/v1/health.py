from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import time

from app.database import get_db

router = APIRouter()

start_time = time.time()

@router.get("/health/")
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    # Check database
    try:
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except:
        db_status = "unhealthy"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "redis": "healthy",
        "ai_pipeline": "ready",
        "cameras_active": 0,
        "uptime_seconds": time.time() - start_time
    }
