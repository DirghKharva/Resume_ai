import logging
import docx

logger = logging.getLogger(__name__)

def extract_text_from_docx(file_path: str) -> str:
    """
    Extracts raw text from a DOCX file using python-docx.
    
    Args:
        file_path (str): The local path to the DOCX file.
        
    Returns:
        str: The extracted raw text, stripped of leading/trailing whitespace.
        
    Raises:
        FileNotFoundError: If the file does not exist.
        Exception: For other errors encountered during DOCX parsing.
    """
    extracted_text = []
    
    try:
        doc = docx.Document(file_path)
        
        # Extract text from paragraphs
        for para in doc.paragraphs:
            if para.text.strip():
                extracted_text.append(para.text)
                
        # Extract text from tables to ensure we don't miss structured experience details
        for table in doc.tables:
            for row in table.rows:
                row_text = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_text:
                    # Join cell contents within a row with a separator, e.g., " | "
                    extracted_text.append(" | ".join(row_text))
                    
    except FileNotFoundError:
        logger.error(f"DOCX file not found at path: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Failed to parse DOCX file at {file_path}: {str(e)}")
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")
        
    return "\n\n".join(extracted_text).strip()
