import os
import shutil
import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.graph.parallel_graph import parallel_graph
from app.graph.enhancement_graph import enhance_resume

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "outputs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ─────────────────────────────────────────────
# Request / Response Models
# ─────────────────────────────────────────────

class EnhanceRequest(BaseModel):
    """
    Request body for the /enhance endpoint.
    All Phase 1 analysis results + user's answers to follow-up questions.
    """
    resume_path: str                           # Path to the saved .docx in uploads/
    target_role: str
    job_description: Optional[str] = ""
    user_answers: Dict[str, str] = {}          # { question: user_answer }
    parsed_resume: Dict[str, Any] = {}
    ats_result: Dict[str, Any] = {}
    recruiter_result: Dict[str, Any] = {}
    grammar_result: Dict[str, Any] = {}
    project_result: Dict[str, Any] = {}
    keyword_result: Dict[str, Any] = {}


class EnhanceResponse(BaseModel):
    """
    Response from the /enhance endpoint.
    """
    enhanced_file_path: str
    enhancements_made: list[str]
    agent_log: list[str] = []
    error: Optional[str] = None


# ─────────────────────────────────────────────
# Phase 1: Analyze Resume
# ─────────────────────────────────────────────

@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    target_role: str = Form(...),
    job_description: Optional[str] = Form(None)
):
    """
    Upload a resume file and run the multi-agent analysis graph.

    Changes from original:
    - File is NOW KEPT after analysis (not deleted) so /enhance can use it
    - resume_path is included in the response so the frontend can pass it to /enhance
    """
    filename = file.filename or "resume"
    ext = os.path.splitext(filename)[1].lower()

    if ext not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Only PDF and DOCX are supported."
        )

    # Save the uploaded file — we keep it (not temp) so /enhance can use it
    saved_path = os.path.join(UPLOAD_DIR, filename)
    try:
        with open(saved_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved uploaded file to {saved_path}")
    except Exception as e:
        logger.error(f"Failed to save file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Run the parallel LangGraph analysis pipeline
    try:
        initial_state = {
            "resume_path": saved_path,
            "target_role": target_role,
            "job_description": job_description or "",
            "raw_resume_text": "",
            "parsed_resume": {}
        }

        logger.info("Invoking parallel resume analysis graph...")
        final_state = parallel_graph.invoke(initial_state)

        if "aggregated_result" not in final_state:
            raise HTTPException(
                status_code=500,
                detail="Orchestration graph failed to synthesize results."
            )

        # Include resume_path in response so frontend passes it to /enhance
        final_state["resume_path"] = saved_path
        return final_state

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        # Clean up the saved file if analysis fails
        if os.path.exists(saved_path):
            os.remove(saved_path)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


# ─────────────────────────────────────────────
# Phase 2: Enhance Resume
# ─────────────────────────────────────────────

@router.post("/enhance", response_model=EnhanceResponse)
async def enhance_resume_endpoint(request: EnhanceRequest):
    """
    Phase 2: Enhance the resume using a LangGraph ReAct agent + Office-Word-MCP-Server.

    The agent autonomously:
    - Reads the current .docx file
    - Applies improvements using 30+ Word document MCP tools
    - Preserves original fonts, formatting and layout
    - Saves the result to outputs/enhanced_{filename}.docx

    Only .docx files are supported. If a PDF was uploaded, returns an error.
    """
    resume_path = request.resume_path

    # Validate the file still exists
    if not os.path.exists(resume_path):
        raise HTTPException(
            status_code=404,
            detail=f"Resume file not found at {resume_path}. Please re-upload."
        )

    # Only DOCX files can be edited in-place
    if not resume_path.lower().endswith(".docx"):
        raise HTTPException(
            status_code=400,
            detail=(
                "Resume enhancement requires a .docx (Word) file. "
                "PDF files cannot be edited in-place. "
                "Please re-upload your resume as a Word document."
            )
        )

    # Build the state dict the enhancement graph expects
    state = {
        "resume_path": resume_path,
        "target_role": request.target_role,
        "job_description": request.job_description or "",
        "user_answers": request.user_answers,
        "parsed_resume": request.parsed_resume,
        "ats_result": request.ats_result,
        "recruiter_result": request.recruiter_result,
        "grammar_result": request.grammar_result,
        "project_result": request.project_result,
        "keyword_result": request.keyword_result,
    }

    try:
        logger.info(f"Starting Phase 2 enhancement for: {resume_path}")
        result = enhance_resume(state)

        if result.get("error"):
            raise HTTPException(status_code=400, detail=result["error"])

        logger.info(
            f"Enhancement complete. File: {result['enhanced_file_path']}. "
            f"Changes: {len(result['enhancements_made'])}"
        )
        return EnhanceResponse(**result)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Enhancement failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Enhancement failed: {str(e)}")


# ─────────────────────────────────────────────
# Download Enhanced Resume
# ─────────────────────────────────────────────

@router.get("/download/{filename}")
async def download_enhanced_resume(filename: str):
    """
    Download the enhanced resume file from the outputs/ directory.

    Called by the Streamlit frontend's download button.
    Example: GET /api/v1/download/enhanced_resume.docx
    """
    file_path = os.path.join(OUTPUT_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"File '{filename}' not found in outputs directory."
        )

    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


# ─────────────────────────────────────────────
# Cleanup
# ─────────────────────────────────────────────

@router.delete("/cleanup/{filename}")
async def cleanup_file(filename: str):
    """
    Delete a saved resume from the uploads/ directory.
    Call this when the user is done with Phase 2 to free disk space.
    """
    file_path = os.path.join(UPLOAD_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File '{filename}' not found.")

    try:
        os.remove(file_path)
        logger.info(f"Cleaned up uploaded file: {file_path}")
        return {"message": f"File '{filename}' deleted successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")
