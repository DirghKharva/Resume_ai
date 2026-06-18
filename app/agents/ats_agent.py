import json
import logging
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from app.models.state import ResumeState
from app.models.agent_outputs import ATSAgentOutput
from app.prompts import get_ats_prompt_template


logger = logging.getLogger(__name__)

def ats_agent(state: ResumeState) -> Dict[str, Any]:
    """
    ATS Agent Node. Analyzes formatting, structure, and keywords of a resume.
    
    Args:
        state (ResumeState): The current LangGraph state.
        
    Returns:
        dict: A dictionary updating the state with 'ats_result'.
    """
    logger.info("ATS Agent processing resume...")
    raw_text = state.get("raw_resume_text", "")
    parsed_resume = state.get("parsed_resume", {})
    
    if not raw_text.strip():
        logger.warning("No raw resume text provided to ATS Agent.")
        return {
            "ats_result": {
                "score": 0,
                "issues": ["No resume content found to analyze."],
                "suggestions": ["Please upload a valid resume."]
            }
        }
        
    try:
        # Load prompt template
        prompt_template = get_ats_prompt_template()
        
        # Format parsed resume to pretty JSON string for context
        parsed_resume_str = json.dumps(parsed_resume, indent=2)
        
        # Initialize LLM with structured output configuration
        from app.parser.structured_parser import get_llm
        llm = get_llm(model_name="gemini-2.5-flash", temperature=0.0)
        structured_llm = llm.with_structured_output(ATSAgentOutput)
        
        # Define chat prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a specialized AI agent focused on resume ATS compatibility."),
            ("user", prompt_template)
        ])
        
        # Create chain
        chain = prompt | structured_llm
        
        # Execute
        result: ATSAgentOutput = chain.invoke({
            "raw_resume_text": raw_text,
            "parsed_resume": parsed_resume_str
        })
        
        logger.info("ATS Agent analysis successfully complete.")
        return {"ats_result": result.model_dump()}
        
    except Exception as e:
        logger.error(f"Error in ATS Agent execution: {str(e)}")
        # Graceful fallback to prevent graph pipeline breakdown
        return {
            "ats_result": {
                "score": 50,
                "issues": [f"Error occurred during ATS analysis: {str(e)}"],
                "suggestions": ["Retry the analysis or verify the Gemini API configuration."]
            }
        }
