import pytest
import os
from dotenv import load_dotenv
from app.agents.recruiter_agent import recruiter_agent
from app.models.state import ResumeState

# Ensure environment variables are loaded
load_dotenv()

# We only run integration tests if GOOGLE_API_KEY is configured and not a placeholder
HAS_API_KEY = os.getenv("GOOGLE_API_KEY") and not os.getenv("GOOGLE_API_KEY").startswith("your_")

def test_recruiter_agent_empty_resume():
    """Verify that an empty resume is handled gracefully with 0 probability and feedback."""
    state: ResumeState = {
        "raw_resume_text": "",
        "parsed_resume": {}
    }
    
    result = recruiter_agent(state)
    
    assert "recruiter_result" in result
    assert result["recruiter_result"]["shortlist_probability"] == 0
    assert len(result["recruiter_result"]["feedback"]) > 0
    assert "No resume content found" in result["recruiter_result"]["feedback"][0]

@pytest.mark.skipif(not HAS_API_KEY, reason="GOOGLE_API_KEY not configured in .env")
def test_recruiter_agent_good_resume_integration():
    """Verify that a well-formatted professional resume receives a high shortlist probability."""
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

    result = recruiter_agent(state)
    
    assert "recruiter_result" in result
    recruiter = result["recruiter_result"]
    assert "shortlist_probability" in recruiter
    assert isinstance(recruiter["shortlist_probability"], int)
    # A strong developer profile should get a high rating
    assert recruiter["shortlist_probability"] >= 60
    assert isinstance(recruiter["feedback"], list)
    assert len(recruiter["feedback"]) > 0

@pytest.mark.skipif(not HAS_API_KEY, reason="GOOGLE_API_KEY not configured in .env")
def test_recruiter_agent_poor_resume_integration():
    """Verify that a poor resume receives a lower shortlist probability."""
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

    result = recruiter_agent(state)
    
    assert "recruiter_result" in result
    recruiter = result["recruiter_result"]
    assert "shortlist_probability" in recruiter
    assert isinstance(recruiter["shortlist_probability"], int)
    # Poor resume should score lower
    assert recruiter["shortlist_probability"] < 60
    assert len(recruiter["feedback"]) > 0
