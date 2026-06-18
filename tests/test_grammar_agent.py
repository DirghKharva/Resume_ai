import pytest
import os
from dotenv import load_dotenv
from app.agents.grammar_agent import grammar_agent
from app.models.state import ResumeState

# Ensure environment variables are loaded
load_dotenv()

# We only run integration tests if GOOGLE_API_KEY is configured and not a placeholder
HAS_API_KEY = os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_API_KEY").startswith("your_")

def test_grammar_agent_empty_resume():
    """Verify that an empty resume is handled gracefully with score 0 and error feedback."""
    state: ResumeState = {
        "raw_resume_text": "",
        "parsed_resume": {}
    }
    
    result = grammar_agent(state)
    
    assert "grammar_result" in result
    assert result["grammar_result"]["score"] == 0
    assert len(result["grammar_result"]["errors"]) > 0
    assert "No resume content found" in result["grammar_result"]["errors"][0]

@pytest.mark.skipif(not HAS_API_KEY, reason="GOOGLE_API_KEY not configured in .env")
def test_grammar_agent_good_resume_integration():
    """Verify that a grammatically correct resume receives a high score and zero or few errors."""
    good_raw_text = """
    JOHN DOE
    Email: john.doe@email.com | Phone: (123) 456-7890 | Location: San Francisco, CA

    PROFESSIONAL SUMMARY
    Experienced Software Engineer with 5+ years of experience designing and building scalable web applications using Python, Django, and React. Proven track record of improving application performance and leading small engineering teams.

    PROFESSIONAL EXPERIENCE
    Senior Software Engineer | Tech Solutions Inc. | Jan 2022 - Present
    - Designed and implemented a microservices-based backend API using FastAPI.
    - Led a team of 3 developers to rebuild the legacy Django platform.
    - Optimized PostgreSQL queries and database indexing.

    Software Engineer | App Creators Corp | Jun 2019 - Dec 2021
    - Developed and maintained web applications using React and Django.
    - Automated CI/CD deployment pipeline using Docker and GitHub Actions.
    """

    good_parsed = {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "(123) 456-7890",
        "location": "San Francisco, CA",
        "skills": ["Python", "FastAPI", "Django", "React", "Docker", "PostgreSQL"],
        "experience": [
            {
                "company": "Tech Solutions Inc.",
                "role": "Senior Software Engineer",
                "start_date": "Jan 2022",
                "end_date": "Present",
                "description": [
                    "Designed and implemented a microservices-based backend API using FastAPI.",
                    "Led a team of 3 developers to rebuild the legacy Django platform.",
                    "Optimized PostgreSQL queries."
                ]
            },
            {
                "company": "App Creators Corp",
                "role": "Software Engineer",
                "start_date": "Jun 2019",
                "end_date": "Dec 2021",
                "description": [
                    "Developed and maintained web applications using React and Django.",
                    "Automated CI/CD deployment pipeline using Docker."
                ]
            }
        ]
    }

    state: ResumeState = {
        "raw_resume_text": good_raw_text,
        "parsed_resume": good_parsed
    }

    result = grammar_agent(state)
    
    assert "grammar_result" in result
    grammar = result["grammar_result"]
    assert "score" in grammar
    assert isinstance(grammar["score"], int)
    assert grammar["score"] >= 80
    assert isinstance(grammar["errors"], list)
    assert isinstance(grammar["suggestions"], list)

@pytest.mark.skipif(not HAS_API_KEY, reason="GOOGLE_API_KEY not configured in .env")
def test_grammar_agent_poor_resume_integration():
    """Verify that a resume with spelling mistakes and tense inconsistencies gets a lower score."""
    poor_raw_text = """
    BOB SMITH
    email - bob@email.com
    
    ABOUT ME
    I is a software developer with experience in python. i like building web sites.
    
    EXPERIENCE
    Python dev | WebCo | Jan 2018 - Dec 2020
    - I build and writes code using python and django. (Tense inconsistency: present tense in past job)
    - I am responible for fixing bugs. (Spelling error: responible)
    - create database structures.
    """

    poor_parsed = {
        "name": "Bob Smith",
        "email": "bob@email.com",
        "skills": ["python", "django"],
        "experience": [
            {
                "company": "WebCo",
                "role": "Python dev",
                "start_date": "Jan 2018",
                "end_date": "Dec 2020",
                "description": [
                    "I build and writes code using python and django.",
                    "I am responible for fixing bugs.",
                    "create database structures."
                ]
            }
        ]
    }

    state: ResumeState = {
        "raw_resume_text": poor_raw_text,
        "parsed_resume": poor_parsed
    }

    result = grammar_agent(state)
    
    assert "grammar_result" in result
    grammar = result["grammar_result"]
    assert "score" in grammar
    assert isinstance(grammar["score"], int)
    # Poor grammar should score lower
    assert grammar["score"] < 80
    assert len(grammar["errors"]) > 0
    assert len(grammar["suggestions"]) > 0
