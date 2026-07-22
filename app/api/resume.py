import os
import shutil
import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.graph.parallel_graph import parallel_graph

logger = logging.getLogger(__name__)

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/analyze")
async def analyze_resume(
    file: UploadFile = File(...),
    target_role: str = Form(...),
    job_description: Optional[str] = Form(None)
):
    """
    Upload a resume file and run the multi-agent orchestration graph analysis.
    """
    filename = file.filename or "resume"
    ext = os.path.splitext(filename)[1].lower()
    
    if ext not in [".pdf", ".docx", ".doc"]:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Only PDF and DOCX are supported."
        )

    # Save the file temporarily
    temp_file_path = os.path.join(UPLOAD_DIR, f"temp_{filename}")
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Saved temporary file to {temp_file_path} for analysis.")
    except Exception as e:
        logger.error(f"Failed to save temporary file: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

    # Run the parallel LangGraph analysis pipeline
    try:
        initial_state = {
            "resume_path": temp_file_path,
            "target_role": target_role,
            "job_description": job_description or "",
            "raw_resume_text": "",
            "parsed_resume": {}
        }
        
        logger.info("Invoking parallel resume analysis graph...")
        final_state = parallel_graph.invoke(initial_state)
        
        # Verify result was produced
        if "aggregated_result" not in final_state:
            raise HTTPException(status_code=500, detail="Orchestration graph failed to synthesize results.")

        return final_state
    except Exception as e:
        logger.error(f"Analysis failed during graph invocation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        # Clean up the file
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as cleanup_err:
                logger.warning(f"Failed to delete temp file {temp_file_path}: {str(cleanup_err)}")
