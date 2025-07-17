"""
Main FastAPI application for Orca Job Orchestrator.
Configures the API server with all routes, middleware, and dependencies.
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import settings
from ..core.database import init_database, close_database, get_db_session, DatabaseHealthCheck
from ..core.security import get_current_user_optional
from .routers import auth, systems, jobs

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Orca Job Orchestrator API...")
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized successfully")
        
        # TODO: Start background health checks
        # TODO: Initialize execution engine monitoring
        
        yield
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Orca Job Orchestrator API...")
        
        try:
            # Close database connections
            await close_database()
            logger.info("Database connections closed")
            
            # TODO: Shutdown execution engine gracefully
            
        except Exception as e:
            logger.error(f"Shutdown error: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "error_type": type(exc).__name__
        }
    )


# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(systems.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")


# Health check endpoints
@app.get("/health", tags=["health"])
async def health_check() -> dict:
    """
    Basic health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "orca-job-orchestrator",
        "version": settings.api_version
    }


@app.get("/health/detailed", tags=["health"])
async def detailed_health_check(
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Detailed health check including database connectivity.
    
    Args:
        db: Database session
        
    Returns:
        Detailed health status
    """
    try:
        # Check database connection
        db_health = await DatabaseHealthCheck.check_connection()
        db_info = await DatabaseHealthCheck.get_connection_info()
        
        # TODO: Check execution engine health
        # execution_health = await execution_engine.health_check()
        
        return {
            "status": "healthy" if db_health else "unhealthy",
            "service": "orca-job-orchestrator",
            "version": settings.api_version,
            "database": db_info,
            "components": {
                "database": "healthy" if db_health else "unhealthy",
                "execution_engine": "healthy"  # TODO: Get actual status
            }
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "orca-job-orchestrator",
            "version": settings.api_version,
            "error": str(e)
        }


@app.get("/api/dashboard", tags=["dashboard"])
async def dashboard(
    current_user: dict = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db_session)
) -> dict:
    """
    Dashboard endpoint with system and job statistics.
    
    Args:
        current_user: Optional current user
        db: Database session
        
    Returns:
        Dashboard data
    """
    try:
        from ..services.system_service import SystemService
        from ..services.job_service import JobService
        from ..services.execution_engine import execution_engine
        
        # Get statistics
        system_stats = await SystemService.get_system_stats(db)
        job_stats = await JobService.get_job_stats(db)
        execution_stats = await JobService.get_execution_stats(db)
        
        # Get running jobs info
        running_jobs = await execution_engine.get_running_jobs()
        engine_health = await execution_engine.health_check()
        
        dashboard_data = {
            "user": {
                "authenticated": current_user is not None,
                "username": current_user.get("username") if current_user else None
            },
            "systems": {
                "total": system_stats.total_systems,
                "active": system_stats.active_systems,
                "healthy": system_stats.healthy_systems,
                "linux": system_stats.linux_systems,
                "windows": system_stats.windows_systems
            },
            "jobs": {
                "total": job_stats.total_jobs,
                "pending": job_stats.pending_jobs,
                "running": job_stats.running_jobs,
                "completed": job_stats.completed_jobs,
                "failed": job_stats.failed_jobs,
                "cancelled": job_stats.cancelled_jobs
            },
            "executions": {
                "total": execution_stats.total_executions,
                "pending": execution_stats.pending_executions,
                "running": execution_stats.running_executions,
                "completed": execution_stats.completed_executions,
                "failed": execution_stats.failed_executions,
                "timeout": execution_stats.timeout_executions,
                "average_duration": execution_stats.average_duration_seconds
            },
            "engine": {
                "status": engine_health["status"],
                "running_jobs": len(running_jobs),
                "available_slots": engine_health["available_slots"]
            }
        }
        
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Dashboard endpoint failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to load dashboard data"
        )


@app.get("/", tags=["root"])
async def root() -> dict:
    """
    Root endpoint with API information.
    
    Returns:
        API information
    """
    return {
        "service": "Orca Job Orchestrator",
        "version": settings.api_version,
        "description": settings.api_description,
        "docs_url": "/docs",
        "health_url": "/health",
        "api_base": "/api"
    }


# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )