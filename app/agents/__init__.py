"""
agents package - Specialized AI agents for resume analysis.

Agents:
    - ATSAgent       : Evaluates ATS compatibility and formatting.
    - RecruiterAgent : Simulates recruiter first-impression review.
    - GrammarAgent   : Checks grammar and readability.
    - ProjectAgent   : Analyzes technical depth of projects.
    - KeywordAgent   : Identifies missing skills and keywords.
    - QuestionAgent  : Generates intelligent follow-up questions.
    - Aggregator     : Compiles and weights results from all agents.
"""

from app.agents.ats_agent import ats_agent
from app.agents.recruiter_agent import recruiter_agent
from app.agents.grammar_agent import grammar_agent
from app.agents.project_agent import project_agent
from app.agents.keyword_agent import keyword_agent
from app.agents.question_agent import question_agent
from app.agents.aggregator import aggregator

__all__ = [
    "ats_agent",
    "recruiter_agent",
    "grammar_agent",
    "project_agent",
    "keyword_agent",
    "question_agent",
    "aggregator",
]
