import pytest
from unittest.mock import patch, MagicMock
from app.graph import multi_agent_graph
from app.models.state import ResumeState
from app.models.agent_outputs import (
    ATSAgentOutput,
    RecruiterAgentOutput,
    GrammarAgentOutput,
    KeywordAgentOutput,
    QuestionAgentOutput,
)
from app.agents.aggregator import AggregatorLLMOutput

@patch("app.parser.structured_parser.get_llm")
def test_multi_agent_graph_execution(mock_get_llm):
    """Verify that the multi-agent graph compiles and runs all nodes in parallel before compiling aggregated results."""
    # Set up mock LLM and mock chain responses
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    mock_llm.with_structured_output.return_value = mock_structured_llm
    
    # Define mock return objects
    mock_ats = ATSAgentOutput(score=85, issues=["Layout"], suggestions=["Fix Layout"])
    mock_recruiter = RecruiterAgentOutput(shortlist_probability=75, feedback=["Good achievements"])
    mock_grammar = GrammarAgentOutput(score=95, errors=[], suggestions=["Great flow"])
    mock_keyword = KeywordAgentOutput(match_score=70, missing_skills=["AWS"], missing_keywords=[], skill_gaps=["Cloud experience"])
    mock_question = QuestionAgentOutput(questions=["What is the scale?"])
    mock_aggregator = AggregatorLLMOutput(priority_fixes=["Fix Layout", "Add AWS"], dashboard_data={"ats_status": "Good"})
    
    # Configure with_structured_output side_effect to return mocks for different schemas
    def structured_output_side_effect(schema):
        mock_chain = MagicMock()
        mock_val = None
        if schema == ATSAgentOutput:
            mock_val = mock_ats
        elif schema == RecruiterAgentOutput:
            mock_val = mock_recruiter
        elif schema == GrammarAgentOutput:
            mock_val = mock_grammar
        elif schema == KeywordAgentOutput:
            mock_val = mock_keyword
        elif schema == QuestionAgentOutput:
            mock_val = mock_question
        elif schema == AggregatorLLMOutput:
            mock_val = mock_aggregator
            
        mock_chain.invoke.return_value = mock_val
        mock_chain.return_value = mock_val
        return mock_chain
        
    mock_llm.with_structured_output.side_effect = structured_output_side_effect
    
    initial_state: ResumeState = {
        "raw_resume_text": "Alice Smith developer resume",
        "parsed_resume": {"name": "Alice Smith"},
        "target_role": "Python Developer",
        "job_description": "Looking for Python developer with AWS experience."
    }
    
    # Execute graph
    final_state = multi_agent_graph.invoke(initial_state)
    
    # Assert each agent's node successfully populated its state key
    assert "ats_result" in final_state
    assert final_state["ats_result"]["score"] == 85
    
    assert "recruiter_result" in final_state
    assert final_state["recruiter_result"]["shortlist_probability"] == 75
    
    assert "grammar_result" in final_state
    assert final_state["grammar_result"]["score"] == 95
    
    assert "keyword_result" in final_state
    assert final_state["keyword_result"]["match_score"] == 70
    
    assert "question_result" in final_state
    assert "What is the scale?" in final_state["question_result"]["questions"]
    
    # Assert Aggregator computed overall score and synthesized dashboard data
    assert "aggregated_result" in final_state
    # Score calculation check: (85*0.3) + (75*0.3) + (70*0.25) + (95*0.15) = 25.5 + 22.5 + 17.5 + 14.25 = 79.75 -> 79
    assert final_state["aggregated_result"]["overall_score"] == 79
    assert "Fix Layout" in final_state["aggregated_result"]["priority_fixes"]
    assert final_state["aggregated_result"]["dashboard_data"]["ats_status"] == "Good"
