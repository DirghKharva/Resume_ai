import pytest
from unittest.mock import patch, MagicMock
from app.parser import parse_raw_resume_to_structured
from app.models.resume import ParsedResume

@patch("app.parser.structured_parser.get_llm")
def test_parse_raw_resume_to_structured_success(mock_get_llm):
    """Verify that structured parser correctly invokes the LLM chain and returns dict."""
    # Set up mock LLM and mock chain
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    mock_llm.with_structured_output.return_value = mock_structured_llm
    
    # Mock result from LLM invocation
    mock_parsed_resume = ParsedResume(
        name="Alice Smith",
        skills=["Python", "Go"],
        education=[],
        experience=[],
        projects=[],
        certifications=[]
    )
    mock_structured_llm.invoke.return_value = mock_parsed_resume
    mock_structured_llm.return_value = mock_parsed_resume
    
    result = parse_raw_resume_to_structured("Sample raw resume text")
    
    assert result["name"] == "Alice Smith"
    assert "Python" in result["skills"]
    assert "Go" in result["skills"]
    assert isinstance(result, dict)
    
    # Verify that get_llm was called and with_structured_output was configured with ParsedResume
    mock_get_llm.assert_called_once_with(model_name="gemini-2.5-flash", temperature=0.0)
    mock_llm.with_structured_output.assert_called_once_with(ParsedResume)
    mock_structured_llm.assert_called_once()
