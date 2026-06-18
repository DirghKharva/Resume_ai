import pytest
from unittest.mock import patch, MagicMock
from app.graph import parallel_graph
from app.models.state import ResumeState
from app.models.agent_outputs import (
    ATSAgentOutput,
    RecruiterAgentOutput,
    GrammarAgentOutput,
    ProjectAgentOutput,
    KeywordAgentOutput,
    QuestionAgentOutput,
)
from app.agents.aggregator import AggregatorLLMOutput

@patch("app.parser.structured_parser.get_llm")
def test_parallel_graph_execution(mock_get_llm):
    """Verify that the parallel execution graph compiles and runs all nodes in correct sequence:
    START -> parser_node -> parallel agents (6) -> aggregator -> END.
    """
    # Set up mock LLM and mock chain responses
    mock_llm = MagicMock()
    mock_structured_llm = MagicMock()
    mock_get_llm.return_value = mock_llm
    mock_llm.with_structured_output.return_value = mock_structured_llm
    
    # Define mock return objects
    mock_ats = ATSAgentOutput(score=85, issues=["Layout"], suggestions=["Fix Layout"])
    mock_recruiter = RecruiterAgentOutput(shortlist_probability=75, feedback=["Good achievements"])
    mock_grammar = GrammarAgentOutput(score=95, errors=[], suggestions=["Great flow"])
    mock_project = ProjectAgentOutput(score=80, depth_analysis=["Good complexity"], suggestions=[])
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
        elif schema == ProjectAgentOutput:
            mock_val = mock_project
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
    
    # We supply raw_resume_text and parsed_resume so parser_node doesn't try to read paths or hit the LLM parsing endpoint
    initial_state: ResumeState = {
        "raw_resume_text": "Alice Smith developer resume",
        "parsed_resume": {"name": "Alice Smith"},
        "target_role": "Python Developer",
        "job_description": "Looking for Python developer with AWS experience."
    }
    
    # Execute graph
    final_state = parallel_graph.invoke(initial_state)
    
    # Assert parser node output keys
    assert final_state["raw_resume_text"] == "Alice Smith developer resume"
    
    # Assert all agent keys
    assert "ats_result" in final_state
    assert "recruiter_result" in final_state
    assert "grammar_result" in final_state
    assert "project_result" in final_state
    assert "keyword_result" in final_state
    assert "question_result" in final_state
    
    # Assert score calculation:
    # 5 agents: (85*0.25) + (75*0.25) + (70*0.20) + (80*0.15) + (95*0.15) = 21.25 + 18.75 + 14.0 + 12.0 + 14.25 = 80.25 -> 80
    assert "aggregated_result" in final_state
    assert final_state["aggregated_result"]["overall_score"] == 80
    assert "Fix Layout" in final_state["aggregated_result"]["priority_fixes"]
