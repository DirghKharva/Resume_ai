"""
api package - FastAPI route definitions.

Responsible for:
    - Exposing REST endpoints for the resume analyzer.
    - Handling file upload requests.
    - Returning analysis results to the frontend.
"""

from fastapi import APIRouter

router = APIRouter()

# Routes will be registered here as they are built.
# Example: from app.api.resume import router as resume_router
#          router.include_router(resume_router)
