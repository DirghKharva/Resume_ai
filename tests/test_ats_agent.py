import pytest
import os
from dotenv import load_dotenv
from app.agents.ats_agent import ats_agent
from app.models.state import ResumeState

# Ensure environment variables are loaded
load_dotenv()

# We only run integration tests if GOOGLE_API_KEY is configured and not a placeholder
HAS_API_KEY = os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_API_KEY").startswith("your_")

def test_ats_agent_empty_resume():
    """Verify that an empty resume is handled gracefully with score 0 and error messages."""
    state: ResumeState = {
        "raw_resume_text": "",
        "parsed_resume": {}
    }
    
    result = ats_agent(state)
    
    assert "ats_result" in result
    assert result["ats_result"]["score"] == 0
    assert len(result["ats_result"]["issues"]) > 0
    assert "No resume content found" in result["ats_result"]["issues"][0]

@pytest.mark.skipif(not HAS_API_KEY, reason="GOOGLE_API_KEY not configured in .env")
def test_ats_agent_good_resume_integration():
    """Verify that a well-formatted resume receives a high score and few issues."""
    good_raw_text = """
    JOHN DOE
    Email: john.doe@email.com | Phone: (123) 456-7890 | Location: San Francisco, CA
    LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe

    PROFESSIONAL SUMMARY
    Experienced Software Engineer with 5+ years of experience designing and building scalable web applications using Python, Django, and React. Proven track record of improving application performance and leading small engineering teams.

    SKILLS
    Languages: Python, JavaScript, SQL, HTML/CSS
    Frameworks: Django, FastAPI, React, Node.js
    Tools & Databases: Git, Docker, PostgreSQL, AWS, Redis

    PROFESSIONAL EXPERIENCE
    Senior Software Engineer | Tech Solutions Inc. | Jan 2022 - Present
    - Designed and implemented a microservices-based backend API using FastAPI, reducing request latency by 35%.
    - Led a team of 3 developers to rebuild the legacy Django platform, delivering the project 2 weeks ahead of schedule.
    - Optimized PostgreSQL queries and database indexing, reducing CPU usage on database servers by 20%.

    Software Engineer | App Creators Corp | Jun 2019 - Dec 2021
    - Developed and maintained web applications using React and Django, serving over 100,000 monthly active users.
    - Automated CI/CD deployment pipeline using Docker and GitHub Actions, saving developers 5 hours per week.

    EDUCATION
    B.S. in Computer Science | University of California, Berkeley | 2015 - 2019
    """

    good_parsed = {
        "name": "John Doe",
        "email": "john.doe@email.com",
        "phone": "(123) 456-7890",
        "location": "San Francisco, CA",
        "links": ["linkedin.com/in/johndoe", "github.com/johndoe"],
        "summary": "Experienced Software Engineer with 5+ years of experience building web applications.",
        "skills": ["Python", "JavaScript", "SQL", "Django", "FastAPI", "React", "Docker", "PostgreSQL", "AWS"],
        "experience": [
            {
                "company": "Tech Solutions Inc.",
                "role": "Senior Software Engineer",
                "start_date": "Jan 2022",
                "end_date": "Present",
                "description": [
                    "Designed and implemented a microservices-based backend API using FastAPI.",
                    "Led a team of 3 developers to rebuild the legacy Django platform.",
                    "Optimized PostgreSQL queries and database indexing."
                ]
            }
        ],
        "education": [
            {
                "institution": "University of California, Berkeley",
                "degree": "B.S.",
                "field_of_study": "Computer Science",
                "start_date": "2015",
                "end_date": "2019"
            }
        ],
        "projects": [],
        "certifications": []
    }

    state: ResumeState = {
        "raw_resume_text": good_raw_text,
        "parsed_resume": good_parsed
    }

    result = ats_agent(state)
    
    assert "ats_result" in result
    ats = result["ats_result"]
    assert "score" in ats
    assert isinstance(ats["score"], int)
    # A good resume should get a high score
    assert ats["score"] >= 70
    assert isinstance(ats["issues"], list)
    assert isinstance(ats["suggestions"], list)

@pytest.mark.skipif(not HAS_API_KEY, reason="GOOGLE_API_KEY not configured in .env")
def test_ats_agent_poor_resume_integration():
    """Verify that a poorly-formatted resume receives a lower score and identifies formatting issues."""
    poor_raw_text = """
    Resume
    
    Hi I am Bob. I make websites.
    
    My jobs:
    - Code developer at some shop. I wrote code.
    - Helper at grocery store.
    
    Skills:
    - Coding, typing, talking.
    
    Contact: call me at 555-1234.
    """

    poor_parsed = {
        "name": "Bob",
        "email": None,
        "phone": "555-1234",
        "location": None,
        "skills": ["Coding", "typing", "talking"],
        "experience": [
            {"company": "some shop", "role": "Code developer", "description": ["I wrote code"]}
        ],
        "education": []
    }

    state: ResumeState = {
        "raw_resume_text": poor_raw_text,
        "parsed_resume": poor_parsed
    }

    result = ats_agent(state)
    
    assert "ats_result" in result
    ats = result["ats_result"]
    assert "score" in ats
    assert isinstance(ats["score"], int)
    # Poor resume should score significantly lower than the good one
    assert ats["score"] < 70
    # There should be structural issues identified (e.g., missing education, missing email/links)
    assert len(ats["issues"]) > 0
    assert len(ats["suggestions"]) > 0
