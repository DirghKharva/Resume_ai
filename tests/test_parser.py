import pytest
from unittest.mock import patch, MagicMock
from app.parser import parse_resume, extract_text_from_pdf, extract_text_from_docx

def test_parse_resume_unsupported_format():
    """Verify unsupported file extension raises ValueError."""
    with pytest.raises(ValueError, match="Unsupported file format: .txt"):
        parse_resume("resume.txt")

@patch("app.parser.pdf_parser.pdfplumber.open")
def test_extract_text_from_pdf_success(mock_pdf_open):
    """Verify text is extracted correctly from a mocked PDF file."""
    # Set up mock hierarchy
    mock_pdf = MagicMock()
    mock_page1 = MagicMock()
    mock_page1.extract_text.return_type = "Hello page one"
    mock_page1.extract_text.side_effect = None
    mock_page1.extract_text.return_value = "Hello page one"
    
    mock_page2 = MagicMock()
    mock_page2.extract_text.return_value = "Hello page two"
    
    mock_pdf.pages = [mock_page1, mock_page2]
    mock_pdf_open.return_value.__enter__.return_value = mock_pdf

    result = extract_text_from_pdf("resume.pdf")
    assert "Hello page one" in result
    assert "Hello page two" in result
    assert result == "Hello page one\n\nHello page two"

@patch("app.parser.docx_parser.docx.Document")
def test_extract_text_from_docx_success(mock_docx_document):
    """Verify text is extracted correctly from a mocked DOCX file."""
    mock_doc = MagicMock()
    
    # Paragraphs mock
    mock_p1 = MagicMock()
    mock_p1.text = "Hello paragraph one"
    mock_p2 = MagicMock()
    mock_p2.text = "Hello paragraph two"
    mock_doc.paragraphs = [mock_p1, mock_p2]
    
    # Tables mock
    mock_cell1 = MagicMock()
    mock_cell1.text = "Cell 1"
    mock_cell2 = MagicMock()
    mock_cell2.text = "Cell 2"
    mock_row = MagicMock()
    mock_row.cells = [mock_cell1, mock_cell2]
    mock_table = MagicMock()
    mock_table.rows = [mock_row]
    mock_doc.tables = [mock_table]
    
    mock_docx_document.return_value = mock_doc

    result = extract_text_from_docx("resume.docx")
    assert "Hello paragraph one" in result
    assert "Hello paragraph two" in result
    assert "Cell 1 | Cell 2" in result
