from app.models.state import ResumeState

def test_resume_state_keys():
    """Verify that ResumeState structure matches task requirements."""
    # Create an instance matching the state dictionary
    state: ResumeState = {
        "raw_resume_text": "Sample resume text",
        "parsed_resume": {"name": "John Doe", "skills": []},
        "ats_result": {"score": 85},
        "recruiter_result": {"strengths": ["Leadership"]},
        "grammar_result": {"errors": []},
        "project_result": {"depth": "High"},
        "keyword_result": {"missing": []},
        "question_result": {"questions": []},
        "aggregated_result": {"overall_score": 80},
        "user_answers": {"Q1": "A1"},
        "enhanced_resume": {"text": "Improved resume"}
    }
    
    assert state["raw_resume_text"] == "Sample resume text"
    assert state["parsed_resume"]["name"] == "John Doe"
    assert state["ats_result"]["score"] == 85
    assert state["recruiter_result"]["strengths"] == ["Leadership"]
    assert state["grammar_result"]["errors"] == []
    assert state["project_result"]["depth"] == "High"
    assert state["keyword_result"]["missing"] == []
    assert state["question_result"]["questions"] == []
    assert state["aggregated_result"]["overall_score"] == 80
    assert state["user_answers"]["Q1"] == "A1"
    assert state["enhanced_resume"]["text"] == "Improved resume"
