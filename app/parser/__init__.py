"""
parser package - Resume file parsing and structured extraction utilities.

Responsible for:
    - Reading PDF files using pdfplumber.
    - Reading DOCX files using python-docx.
    - Extracting raw text from resume files.
    - Producing structured resume data (JSON/dict) using Gemini.
"""

import os
from app.parser.pdf_parser import extract_text_from_pdf
from app.parser.docx_parser import extract_text_from_docx
from app.parser.structured_parser import parse_raw_resume_to_structured

def parse_resume(file_path: str) -> str:
    """
    Unified entry point for parsing resumes. Determines file type by extension
    and extracts text accordingly.
    
    Args:
        file_path (str): The local path to the resume file.
        
    Returns:
        str: The extracted raw text.
        
    Raises:
        ValueError: If the file format is unsupported.
    """
    _, ext = os.path.splitext(file_path.lower())
    
    if ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Only PDF and DOCX are supported.")

__all__ = [
    "extract_text_from_pdf",
    "extract_text_from_docx",
    "parse_resume",
    "parse_raw_resume_to_structured",
]
