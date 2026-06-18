import pytest
import os
from dotenv import load_dotenv
from app.agents.question_agent import question_agent
from app.models.state import ResumeState

# Ensure environment variables are loaded
load_dotenv()

# We only run integration tests if GOOGLE_API_KEY is configured and not a placeholder
HAS_API_KEY = os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_API_KEY").startswith("your_")

def test_question_agent_empty_resume():
    """Verify that an empty resume is handled gracefully with default fallback questions."""
    state: ResumeState = {
        "raw_resume_text": "",
        "parsed_resume": {}
    }
    
    result = question_agent(state)
    
    assert "question_result" in result
    assert len(result["question_result"]["questions"]) > 0
    assert "upload a valid resume" in result["question_result"]["questions"][0]

@pytest.mark.skipif(not HAS_API_KEY, reason="GOOGLE_API_KEY not configured in .env")
def test_question_agent_integration():
    """Verify that the Question Agent generates specific follow-up questions for a resume."""
    raw_text = """
    JOHN DOE
    Email: john@doe.com

    EXPERIENCE
    Software Developer | WebCorp | 2021 - Present
    - Built a chatbot. (Vague accomplishment)
    - Helped scale the database. (Vague metric)
    """

    parsed = {
        "name": "John Doe",
        "email": "john@doe.com",
        "experience": [
            {
                "company": "WebCorp",
                "role": "Software Developer",
                "start_date": "2021",
                "end_date": "Present",
                "description": ["Built a chatbot.", "Helped scale the database."]
            }
        ]
    }

    state: ResumeState = {
        "raw_resume_text": raw_text,
        "parsed_resume": parsed
    }

    result = question_agent(state)
    
    assert "question_result" in result
    questions = result["question_result"]["questions"]
    assert isinstance(questions, list)
    assert len(questions) >= 3
    # Check that the questions target vague things in the resume
    # The generated questions should be non-empty strings
    for q in questions:
        assert isinstance(q, str)
        assert len(q.strip()) > 0
