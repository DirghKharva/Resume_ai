import logging
import pdfplumber

logger = logging.getLogger(__name__)

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts raw text from a PDF file using pdfplumber.
    
    Args:
        file_path (str): The local path to the PDF file.
        
    Returns:
        str: The extracted raw text, stripped of leading/trailing whitespace.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        Exception: For other errors encountered during PDF parsing.
    """
    extracted_text = []
    
    try:
        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)
                else:
                    logger.warning(f"No text extracted from page {page_num} of {file_path}")
                    
    except FileNotFoundError:
        logger.error(f"PDF file not found at path: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to parse PDF file at {file_path}: {str(e)}")
        raise Exception(f"Failed to extract text from PDF: {str(e)}")
        
    return "\n\n".join(extracted_text).strip()
