import json
import logging
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate

from app.models.state import ResumeState
from app.models.agent_outputs import KeywordAgentOutput
from app.prompts import get_keyword_prompt_template

logger = logging.getLogger(__name__)

def keyword_agent(state: ResumeState) -> Dict[str, Any]:
    """
    Keyword Comparison Agent Node. Evaluates the resume against a target role and
    optional job description to identify missing skills, keywords, and skill gaps.
    
    Args:
        state (ResumeState): The current LangGraph state.
        
    Returns:
        dict: A dictionary updating the state with 'keyword_result'.
    """
    logger.info("Keyword Agent processing resume...")
    raw_text = state.get("raw_resume_text", "")
    parsed_resume = state.get("parsed_resume", {})
    target_role = state.get("target_role", "")
    job_description = state.get("job_description", "")
    
    if not raw_text.strip():
        logger.warning("No raw resume text provided to Keyword Agent.")
        return {
            "keyword_result": {
                "match_score": 0,
                "missing_skills": ["No resume content found to analyze."],
                "missing_keywords": [],
                "skill_gaps": ["Please upload a valid resume."]
            }
        }
        
    if not target_role.strip():
        logger.warning("No target role provided to Keyword Agent. Defaulting to empty comparison.")
        return {
            "keyword_result": {
                "match_score": 0,
                "missing_skills": [],
                "missing_keywords": [],
                "skill_gaps": ["Please specify a target role for keyword comparison."]
            }
        }
        
    try:
        # Load prompt template
        prompt_template = get_keyword_prompt_template()
        
        # Format parsed resume to pretty JSON string for context
        parsed_resume_str = json.dumps(parsed_resume, indent=2)
        
        # Initialize LLM with structured output configuration
        from app.parser.structured_parser import get_llm
        llm = get_llm(model_name="gemini-2.5-flash", temperature=0.0)
        structured_llm = llm.with_structured_output(KeywordAgentOutput)
        
        # Define chat prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a specialized AI career advisor and keyword optimization assistant."),
            ("user", prompt_template)
        ])
        
        # Create chain
        chain = prompt | structured_llm
        
        # Execute
        result: KeywordAgentOutput = chain.invoke({
            "raw_resume_text": raw_text,
            "parsed_resume": parsed_resume_str,
            "target_role": target_role,
            "job_description": job_description or "Not provided"
        })
        
        logger.info("Keyword Agent evaluation successfully complete.")
        return {"keyword_result": result.model_dump()}
        
    except Exception as e:
        logger.error(f"Error in Keyword Agent execution: {str(e)}")
        # Graceful fallback to prevent graph pipeline breakdown
        return {
            "keyword_result": {
                "match_score": 50,
                "missing_skills": [f"Error occurred during keyword comparison: {str(e)}"],
                "missing_keywords": [],
                "skill_gaps": ["Retry the analysis or verify the Gemini API configuration."]
            }
        }
