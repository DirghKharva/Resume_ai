import pytest
import os
from dotenv import load_dotenv
from unittest.mock import patch
from app.agents.aggregator import aggregator
from app.models.state import ResumeState

# Ensure environment variables are loaded
load_dotenv()

# We only run integration tests if GOOGLE_API_KEY is configured and not a placeholder
HAS_API_KEY = os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_API_KEY").startswith("your_")

@patch("app.parser.structured_parser.get_llm")
def test_aggregator_fallback(mock_get_llm):
    """Verify that the aggregator computes overall score and returns fallback fixes on error/empty."""
    mock_get_llm.side_effect = Exception("Simulated LLM error")
    state: ResumeState = {
        "ats_result": {"score": 80, "issues": ["Layout issues"]},
        "recruiter_result": {"shortlist_probability": 70, "feedback": ["Good candidate"]},
        "grammar_result": {"score": 90, "errors": ["typo"]},
        "keyword_result": {"match_score": 60, "missing_skills": ["Docker"]}
    }
    
    # We pass empty raw_resume_text to trigger the fallback logic in LLM call
    state["raw_resume_text"] = ""
    
    result = aggregator(state)
    
    assert "aggregated_result" in result
    agg = result["aggregated_result"]
    
    # Programmatic score check: (80*0.3) + (70*0.3) + (60*0.25) + (90*0.15) = 24 + 21 + 15 + 13.5 = 73.5 -> 73
    assert agg["overall_score"] == 73
    assert len(agg["priority_fixes"]) > 0
    assert "Layout issues" in agg["priority_fixes"][0] or "Docker" in agg["priority_fixes"][0] or "typo" in agg["priority_fixes"][0]
    assert agg["dashboard_data"]["category_scores"]["ats"] == 80

@pytest.mark.skipif(not HAS_API_KEY, reason="GOOGLE_API_KEY not configured in .env")
def test_aggregator_integration():
    """Verify that the aggregator runs a live LLM call to synthesize priority fixes and dashboard statuses."""
    state: ResumeState = {
        "raw_resume_text": "Alice Smith - Resume content.",
        "ats_result": {
            "score": 85,
            "issues": ["Multi-column table detected"],
            "suggestions": ["Convert table layout to standard text flow"]
        },
        "recruiter_result": {
            "shortlist_probability": 75,
            "feedback": ["Strong backend experience, but achievements lack quantitative metrics"]
        },
        "grammar_result": {
            "score": 95,
            "errors": ["Found one minor typo in past experience description"],
            "suggestions": ["Review third paragraph sentence flow"]
        },
        "keyword_result": {
            "match_score": 70,
            "missing_skills": ["AWS", "Docker"],
            "missing_keywords": ["CI/CD pipelines", "Infrastructure as Code"],
            "skill_gaps": ["Lacks container orchestration and cloud architecture experience"]
        }
    }
    
    result = aggregator(state)
    
    assert "aggregated_result" in result
    agg = result["aggregated_result"]
    
    # Programmatic score check: (85*0.3) + (75*0.3) + (70*0.25) + (95*0.15) = 25.5 + 22.5 + 17.5 + 14.25 = 79.75 -> 79
    assert agg["overall_score"] == 79
    assert len(agg["priority_fixes"]) >= 2
    assert "dashboard_data" in agg
    dashboard = agg["dashboard_data"]
    assert "ats_status" in dashboard
    assert "recruiter_status" in dashboard
    assert "grammar_status" in dashboard
    assert "keyword_status" in dashboard
    assert dashboard["category_scores"]["ats"] == 85
