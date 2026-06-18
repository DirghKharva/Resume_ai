from typing import TypedDict, Optional, List, Dict, Any

class ResumeState(TypedDict, total=False):
    """
    Shared state for the JobCopilot AI multi-agent resume analyzer graph.
    
    This dictionary-like object represents the state passed between agents
    in the LangGraph workflow. It stores raw inputs, parsed structures,
    individual agent analysis outputs, and the final aggregated feedback.
    """
    # Raw inputs & Parsing
    resume_path: str               # File path to the uploaded PDF or DOCX resume
    raw_resume_text: str
    parsed_resume: Dict[str, Any]  # Structured representation of the resume
    target_role: str               # Target job title or role
    job_description: str           # Target job description (optional/empty if not provided)
    
    # Agent Analysis Results
    ats_result: Dict[str, Any]
    recruiter_result: Dict[str, Any]
    grammar_result: Dict[str, Any]
    project_result: Dict[str, Any]
    keyword_result: Dict[str, Any]
    question_result: Dict[str, Any]
    
    # Aggregated Outputs & Post-processing
    aggregated_result: Dict[str, Any]
    
    # Future Phases (State preservation)
    user_answers: Dict[str, str]   # Questions mapped to user's answers
    enhanced_resume: Dict[str, Any]  # The revised/enhanced version of the resume
