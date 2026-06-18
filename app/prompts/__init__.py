"""
prompts package - Prompt templates for JobCopilot AI agents and parsing components.
"""

import os

PROMPTS_DIR = os.path.dirname(os.path.abspath(__file__))
ATS_PROMPT_PATH = os.path.join(PROMPTS_DIR, "ats_prompt.txt")
RECRUITER_PROMPT_PATH = os.path.join(PROMPTS_DIR, "recruiter_prompt.txt")
GRAMMAR_PROMPT_PATH = os.path.join(PROMPTS_DIR, "grammar_prompt.txt")
KEYWORD_PROMPT_PATH = os.path.join(PROMPTS_DIR, "keyword_prompt.txt")
QUESTION_PROMPT_PATH = os.path.join(PROMPTS_DIR, "question_prompt.txt")
AGGREGATOR_PROMPT_PATH = os.path.join(PROMPTS_DIR, "aggregator_prompt.txt")
PROJECT_PROMPT_PATH = os.path.join(PROMPTS_DIR, "project_prompt.txt")

from app.prompts.parser_prompts import (
    RESUME_PARSER_SYSTEM_PROMPT,
    RESUME_PARSER_USER_PROMPT_TEMPLATE,
)

def get_ats_prompt_template() -> str:
    """Reads and returns the content of ats_prompt.txt."""
    with open(ATS_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def get_recruiter_prompt_template() -> str:
    """Reads and returns the content of recruiter_prompt.txt."""
    with open(RECRUITER_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def get_grammar_prompt_template() -> str:
    """Reads and returns the content of grammar_prompt.txt."""
    with open(GRAMMAR_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def get_keyword_prompt_template() -> str:
    """Reads and returns the content of keyword_prompt.txt."""
    with open(KEYWORD_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def get_question_prompt_template() -> str:
    """Reads and returns the content of question_prompt.txt."""
    with open(QUESTION_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def get_aggregator_prompt_template() -> str:
    """Reads and returns the content of aggregator_prompt.txt."""
    with open(AGGREGATOR_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

def get_project_prompt_template() -> str:
    """Reads and returns the content of project_prompt.txt."""
    with open(PROJECT_PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()

__all__ = [
    "RESUME_PARSER_SYSTEM_PROMPT",
    "RESUME_PARSER_USER_PROMPT_TEMPLATE",
    "ATS_PROMPT_PATH",
    "RECRUITER_PROMPT_PATH",
    "GRAMMAR_PROMPT_PATH",
    "KEYWORD_PROMPT_PATH",
    "QUESTION_PROMPT_PATH",
    "AGGREGATOR_PROMPT_PATH",
    "PROJECT_PROMPT_PATH",
    "get_ats_prompt_template",
    "get_recruiter_prompt_template",
    "get_grammar_prompt_template",
    "get_keyword_prompt_template",
    "get_question_prompt_template",
    "get_aggregator_prompt_template",
    "get_project_prompt_template",
]
