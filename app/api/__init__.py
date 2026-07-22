"""
api package - FastAPI route definitions.

Responsible for:
    - Exposing REST endpoints for the resume analyzer.
    - Handling file upload requests.
    - Returning analysis results to the frontend.
"""

from fastapi import APIRouter
from app.api.resume import router as resume_router

router = APIRouter()

router.include_router(resume_router)
