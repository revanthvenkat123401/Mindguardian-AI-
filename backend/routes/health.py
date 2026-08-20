"""Health check and system status routes"""
from fastapi import APIRouter, Depends
from datetime import datetime
from database import SessionLocal
from cache import CacheService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/health", tags=["health"])


@router.get("/status")
async def health_check():
    """
    Health check endpoint - checks all services
    """
    status_info = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }
    
    # Check database
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        status_info["services"]["database"] = "ok"
    except Exception as e:
        status_info["services"]["database"] = f"error: {str(e)}"
        status_info["status"] = "degraded"
    
    # Check Redis
    try:
        if CacheService._redis:
            await CacheService._redis.ping()
            status_info["services"]["cache"] = "ok"
        else:
            status_info["services"]["cache"] = "not_initialized"
    except Exception as e:
        status_info["services"]["cache"] = f"error: {str(e)}"
        status_info["status"] = "degraded"
    
    return status_info


@router.get("/")
async def root():
    """
    API information
    """
    return {
        "name": "MindGuardian AI Backend",
        "version": "1.0.0",
        "description": "Privacy-first cognitive monitoring backend",
        "endpoints": {
            "users": "/api/v1/users",
            "sessions": "/api/v1/sessions",
            "decisions": "/api/v1/decisions",
            "analytics": "/api/v1/analytics",
            "health": "/api/v1/health",
            "docs": "/docs"
        }
    }
