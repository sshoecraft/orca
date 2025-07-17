#!/usr/bin/env python3
"""
Orca Job Orchestrator startup script.
Runs the FastAPI application with proper configuration.
"""

import uvicorn
import sys
import os

# Add backend to Python path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )