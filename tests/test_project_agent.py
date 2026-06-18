import pytest
import os
from dotenv import load_dotenv
from app.agents.project_agent import project_agent
from app.models.state import ResumeState

# Ensure environment variables are loaded
load_dotenv()

# We only run integration tests if GOOGLE_API_KEY is configured and not a placeholder
HAS_API_KEY = os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_API_KEY").startswith("your_")

def test_project_agent_empty_resume():
    """Verify that an empty resume is handled gracefully with score 0 and fallback analysis."""
    state: ResumeState = {
        "raw_resume_text": "",
        "parsed_resume": {}
    }
    
    result = project_agent(state)
    
    assert "project_result" in result
    assert result["project_result"]["score"] == 0
    assert len(result["project_result"]["depth_analysis"]) > 0
    assert "No projects found" in result["project_result"]["depth_analysis"][0]

@pytest.mark.skipif(not HAS_API_KEY, reason="GOOGLE_API_KEY not configured in .env")
def test_project_agent_integration():
    """Verify that a realistic project list generates technical analysis and score."""
    raw_text = """
    JOHN DOE
    
    PROJECTS
    Distributed Cache | Lead | Python, Redis, Docker
    - Built a distributed in-memory cache system in Python using Redis for caching key-value structures.
    - Containerized with Docker and scaled across 3 nodes using Docker Compose.
    - Added asynchronous write-back mechanism using Celery to persist cache misses to PostgreSQL.
    """

    parsed = {
        "name": "John Doe",
        "projects": [
            {
                "title": "Distributed Cache",
                "technologies": ["Python", "Redis", "Docker", "Celery", "PostgreSQL"],
                "description": [
                    "Built a distributed in-memory cache system in Python.",
                    "Containerized with Docker and scaled across 3 nodes.",
                    "Added asynchronous write-back mechanism using Celery to persist cache misses to PostgreSQL."
                ]
            }
        ]
    }

    state: ResumeState = {
        "raw_resume_text": raw_text,
        "parsed_resume": parsed
    }

    result = project_agent(state)
    
    assert "project_result" in result
    project = result["project_result"]
    assert "score" in project
    assert isinstance(project["score"], int)
    assert project["score"] >= 60
    assert len(project["depth_analysis"]) > 0
    assert len(project["suggestions"]) > 0
