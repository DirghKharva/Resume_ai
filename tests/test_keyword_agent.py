import pytest
import os
from dotenv import load_dotenv
from app.agents.keyword_agent import keyword_agent
from app.models.state import ResumeState

# Ensure environment variables are loaded
load_dotenv()

# We only run integration tests if GOOGLE_API_KEY is configured and not a placeholder
HAS_API_KEY = os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_API_KEY").startswith("your_")

def test_keyword_agent_empty_inputs():
    """Verify that an empty resume/input is handled gracefully."""
    state: ResumeState = {
        "raw_resume_text": "",
        "parsed_resume": {},
        "target_role": "Python Developer",
        "job_description": ""
    }
    
    result = keyword_agent(state)
    
    assert "keyword_result" in result
    assert result["keyword_result"]["match_score"] == 0
    assert "No resume content found" in result["keyword_result"]["missing_skills"][0]

def test_keyword_agent_missing_target_role():
    """Verify that a missing target role returns a validation suggestion."""
    state: ResumeState = {
        "raw_resume_text": "Bob Smith developer resume",
        "parsed_resume": {"name": "Bob Smith"},
        "target_role": "",
        "job_description": ""
    }
    
    result = keyword_agent(state)
    
    assert "keyword_result" in result
    assert result["keyword_result"]["match_score"] == 0
    assert "Please specify a target role" in result["keyword_result"]["skill_gaps"][0]

@pytest.mark.skipif(not HAS_API_KEY, reason="GOOGLE_API_KEY not configured in .env")
def test_keyword_agent_matching_role_integration():
    """Verify that a candidate matching the target role receives a high match score and small skill gaps."""
    good_raw_text = """
    JOHN DOE
    Email: john.doe@email.com | Phone: (123) 456-7890 | Location: San Francisco, CA

    PROFESSIONAL SUMMARY
    Senior Software Engineer with 5+ years of experience designing and building scalable web applications using Python, Django, and React.

    SKILLS
    Python, JavaScript, SQL, Django, FastAPI, React, Docker, PostgreSQL, AWS, Redis

    PROFESSIONAL EXPERIENCE
    Senior Software Engineer | Tech Solutions Inc. | Jan 2022 - Present
    - Designed and implemented a microservices-based backend API using FastAPI.
    - Led a team of 3 developers to rebuild the legacy Django platform.
    """

    good_parsed = {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "skills": ["Python", "JavaScript", "SQL", "Django", "FastAPI", "React", "Docker", "PostgreSQL", "AWS"],
        "experience": [
            {
                "company": "Tech Solutions Inc.",
                "role": "Senior Software Engineer",
                "start_date": "Jan 2022",
                "end_date": "Present",
                "description": ["Designed and implemented a microservices-based backend API using FastAPI."]
            }
        ]
    }

    state: ResumeState = {
        "raw_resume_text": good_raw_text,
        "parsed_resume": good_parsed,
        "target_role": "Senior Full-Stack Python Developer",
        "job_description": "Looking for a developer with expertise in Python, Django, React, AWS, Docker and SQL to build high-performance web systems."
    }

    result = keyword_agent(state)
    
    assert "keyword_result" in result
    kw = result["keyword_result"]
    assert "match_score" in kw
    assert isinstance(kw["match_score"], int)
    # Good match should get a high score
    assert kw["match_score"] >= 70
    assert isinstance(kw["missing_skills"], list)
    assert isinstance(kw["missing_keywords"], list)
    assert isinstance(kw["skill_gaps"], list)

@pytest.mark.skipif(not HAS_API_KEY, reason="GOOGLE_API_KEY not configured in .env")
def test_keyword_agent_mismatched_role_integration():
    """Verify that a candidate mismatching the target role receives a low match score and identified gaps."""
    poor_raw_text = """
    BOB SMITH
    email - bob@email.com
    
    ABOUT ME
    I am a retail cashier with experience in handling checkouts and helping customers.
    
    EXPERIENCE
    Cashier | Grocery Mart | Jan 2018 - Present
    - Checked out customer groceries.
    - Balanced cash register daily.
    """

    poor_parsed = {
        "name": "Bob Smith",
        "email": "bob@email.com",
        "skills": ["Customer service", "Cash handling"],
        "experience": [
            {
                "company": "Grocery Mart",
                "role": "Cashier",
                "start_date": "Jan 2018",
                "end_date": "Present",
                "description": ["Checked out customer groceries.", "Balanced cash register daily."]
            }
        ]
    }

    state: ResumeState = {
        "raw_resume_text": poor_raw_text,
        "parsed_resume": poor_parsed,
        "target_role": "Senior Cloud Infrastructure Architect",
        "job_description": "Architect cloud environments, manage Kubernetes clusters, design secure network layouts, and automate infrastructure deployments using Terraform."
    }

    result = keyword_agent(state)
    
    assert "keyword_result" in result
    kw = result["keyword_result"]
    assert "match_score" in kw
    assert isinstance(kw["match_score"], int)
    # A retail cashier applying for a Senior Cloud Architect role should score very low
    assert kw["match_score"] < 40
    # There should be significant skill gaps identified
    assert len(kw["missing_skills"]) > 0
    assert len(kw["skill_gaps"]) > 0
