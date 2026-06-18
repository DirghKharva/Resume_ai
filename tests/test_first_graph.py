import pytest
from unittest.mock import patch, MagicMock
from app.graph import first_graph
from app.models.state import ResumeState
from app.models.agent_outputs import ATSAgentOutput

@patch("app.parser.structured_parser.get_llm")
def test_first_graph_execution(mock_get_llm):
    """Verify that the compiled LangGraph workflow starts, runs the ats_agent node, and reaches END."""
    # Mock LLM and structured output
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    mock_llm.with_structured_output.return_value = mock_structured_llm
    
    # Mock return value of structured LLM
    mock_ats_output = ATSAgentOutput(
        score=90,
        issues=["Vague bullet points"],
        suggestions=["Add metrics"]
    )
    mock_structured_llm.invoke.return_value = mock_ats_output
    mock_structured_llm.return_value = mock_ats_output

    initial_state: ResumeState = {
        "raw_resume_text": "Jane Doe - Python engineer resume text",
        "parsed_resume": {"name": "Jane Doe", "skills": ["Python"]}
    }
    
    # Run the graph
    final_state = first_graph.invoke(initial_state)
    
    # Assertions
    assert "ats_result" in final_state
    assert final_state["ats_result"]["score"] == 90
    assert "Vague bullet points" in final_state["ats_result"]["issues"]
    
    # Verify mock calls
    mock_get_llm.assert_called_once()
    mock_llm.with_structured_output.assert_called_once_with(ATSAgentOutput)
    mock_structured_llm.assert_called_once()
