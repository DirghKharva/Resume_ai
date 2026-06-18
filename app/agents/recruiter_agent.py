import json
import logging
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate

from app.models.state import ResumeState
from app.models.agent_outputs import RecruiterAgentOutput
from app.prompts import get_recruiter_prompt_template

logger = logging.getLogger(__name__)

def recruiter_agent(state: ResumeState) -> Dict[str, Any]:
    """
    Recruiter Agent Node. Evaluates the resume from a recruiter's perspective,
    judging presentation, strengths, missing metrics, and shortlist likelihood.
    
    Args:
        state (ResumeState): The current LangGraph state.
        
    Returns:
        dict: A dictionary updating the state with 'recruiter_result'.
    """
    logger.info("Recruiter Agent processing resume...")
    raw_text = state.get("raw_resume_text", "")
    parsed_resume = state.get("parsed_resume", {})
    
    if not raw_text.strip():
        logger.warning("No raw resume text provided to Recruiter Agent.")
        return {
            "recruiter_result": {
                "shortlist_probability": 0,
                "feedback": ["No resume content found to evaluate."]
            }
        }
        
    try:
        # Load prompt template
        prompt_template = get_recruiter_prompt_template()
        
        # Format parsed resume to pretty JSON string for context
        parsed_resume_str = json.dumps(parsed_resume, indent=2)
        
        # Initialize LLM with structured output configuration
        from app.parser.structured_parser import get_llm
        llm = get_llm(model_name="gemini-2.5-flash", temperature=0.0)
        structured_llm = llm.with_structured_output(RecruiterAgentOutput)
        
        # Define chat prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a specialized AI recruiter focused on technical talent evaluation."),
            ("user", prompt_template)
        ])
        
        # Create chain
        chain = prompt | structured_llm
        
        # Execute
        result: RecruiterAgentOutput = chain.invoke({
            "raw_resume_text": raw_text,
            "parsed_resume": parsed_resume_str
        })
        
        logger.info("Recruiter Agent evaluation successfully complete.")
        return {"recruiter_result": result.model_dump()}
        
    except Exception as e:
        logger.error(f"Error in Recruiter Agent execution: {str(e)}")
        # Graceful fallback to prevent graph pipeline breakdown
        return {
            "recruiter_result": {
                "shortlist_probability": 50,
                "feedback": [f"Error occurred during recruiter analysis: {str(e)}"]
            }
        }
