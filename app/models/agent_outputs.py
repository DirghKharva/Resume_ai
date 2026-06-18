from typing import List, Dict, Any
from pydantic import BaseModel, Field

class ATSAgentOutput(BaseModel):
    """Structured output from the ATS Analysis Agent."""
    score: int = Field(
        description="ATS compatibility score (0-100) based on formatting, structure, and keyword completeness."
    )
    issues: List[str] = Field(
        default_factory=list,
        description="List of identified issues (e.g., non-standard section headers, complex table structures, missing contact details)."
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Actionable suggestions to resolve the identified issues and improve ATS score."
    )

class RecruiterAgentOutput(BaseModel):
    """Structured output from the Recruiter Evaluation Agent."""
    shortlist_probability: int = Field(
        description="Probability (0-100) that a recruiter would shortlist this candidate for an interview."
    )
    feedback: List[str] = Field(
        default_factory=list,
        description="Detailed feedback from a recruiter's perspective, including first impression, candidate strengths, and missing achievements."
    )

class GrammarAgentOutput(BaseModel):
    """Structured output from the Grammar and Readability Agent."""
    score: int = Field(
        description="Overall readability and grammar quality score (0-100)."
    )
    errors: List[str] = Field(
        default_factory=list,
        description="Specific list of spelling, grammar, punctuation, or tense consistency errors."
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Suggestions to improve writing style, sentence flow, action verb usage, and readability."
    )

class KeywordAgentOutput(BaseModel):
    """Structured output from the Keyword Comparison Agent."""
    match_score: int = Field(
        description="Overall keyword and skill alignment score (0-100) compared to target role."
    )
    missing_skills: List[str] = Field(
        default_factory=list,
        description="Core technical or soft skills that are missing but required for the target role."
    )
    missing_keywords: List[str] = Field(
        default_factory=list,
        description="General industry keywords, technologies, or buzzwords that are absent but highly recommended."
    )
    skill_gaps: List[str] = Field(
        default_factory=list,
        description="Qualitative summary of the gap between the candidate profile and the target job description."
    )

class QuestionAgentOutput(BaseModel):
    """Structured output from the Question Agent."""
    questions: List[str] = Field(
        default_factory=list,
        description="List of intelligent follow-up questions to gather more specific details, metrics, or technologies used in the resume's projects or roles."
    )

class AggregatedResultOutput(BaseModel):
    """Structured output from the Aggregator."""
    overall_score: int = Field(
        description="Overall compatibility score (0-100) calculated as a weighted average of all agent scores."
    )
    priority_fixes: List[str] = Field(
        default_factory=list,
        description="Top 3-5 high-priority, highly actionable fixes compiled across all reports."
    )
    dashboard_data: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured key-value pairs representing metrics and statuses to draw rich visual UI charts."
    )

class ProjectAgentOutput(BaseModel):
    """Structured output from the Project Depth Agent."""
    score: int = Field(
        description="Score (0-100) representing the technical depth and complexity shown in projects."
    )
    depth_analysis: List[str] = Field(
        default_factory=list,
        description="List of observations regarding the architectural complexity, technology choices, and scale of projects."
    )
    suggestions: List[str] = Field(
        default_factory=list,
        description="Specific suggestions to increase project impact, add technical keywords, or showcase deeper system design skills."
    )






