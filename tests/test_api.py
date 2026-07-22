import io
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from main import app

client = TestClient(app)

def test_analyze_endpoint_unsupported_file():
    """Verify that uploading an unsupported file format returns 400 Bad Request."""
    file_content = b"fake file content"
    files = {"file": ("resume.txt", file_content, "text/plain")}
    data = {"target_role": "Python Developer"}
    
    response = client.post("/api/v1/analyze", files=files, data=data)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

@patch("app.api.resume.parallel_graph.invoke")
def test_analyze_endpoint_success(mock_graph_invoke):
    """Verify that a valid PDF file upload invokes the parallel graph and returns results."""
    # Define dummy mock result returned by parallel graph
    dummy_result = {
        "raw_resume_text": "Parsed developer text...",
        "parsed_resume": {"name": "Test Candidate"},
        "ats_result": {"score": 80, "issues": [], "suggestions": []},
        "recruiter_result": {"shortlist_probability": 90, "feedback": ["Looks good"]},
        "grammar_result": {"score": 90, "errors": [], "suggestions": []},
        "project_result": {"score": 85, "depth_analysis": ["Complex"], "suggestions": []},
        "keyword_result": {"match_score": 75, "missing_skills": [], "missing_keywords": [], "skill_gaps": []},
        "question_result": {"questions": []},
        "aggregated_result": {
            "overall_score": 84,
            "priority_fixes": ["Do nothing"],
            "dashboard_data": {"ats_status": "Excellent"}
        }
    }
    mock_graph_invoke.return_value = dummy_result

    # Construct temporary file content matching PDF structure
    file_content = b"%PDF-1.4 mock pdf structure"
    files = {"file": ("my_resume.pdf", file_content, "application/pdf")}
    data = {
        "target_role": "Data Scientist",
        "job_description": "We need someone with machine learning experience."
    }

    response = client.post("/api/v1/analyze", files=files, data=data)
    
    # Assert successful code
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["aggregated_result"]["overall_score"] == 84
    assert res_data["ats_result"]["score"] == 80
    assert res_data["recruiter_result"]["shortlist_probability"] == 90
    
    # Verify graph was invoked
    mock_graph_invoke.assert_called_once()
