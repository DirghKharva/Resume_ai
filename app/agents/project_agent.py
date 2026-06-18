import json
import logging
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate

from app.models.state import ResumeState
from app.models.agent_outputs import ProjectAgentOutput
from app.prompts import get_project_prompt_template

logger = logging.getLogger(__name__)

def project_agent(state: ResumeState) -> Dict[str, Any]:
    """
    Project Depth Agent Node. Evaluates the candidate's projects for technical
    complexity, architectural decisions, and modern system design.
    
    Args:
        state (ResumeState): The current LangGraph state.
        
    Returns:
        dict: A dictionary updating the state with 'project_result'.
    """
    logger.info("Project Depth Agent processing resume...")
    raw_text = state.get("raw_resume_text", "")
    parsed_resume = state.get("parsed_resume", {})
    
    if not raw_text.strip():
        logger.warning("No raw resume text provided to Project Agent.")
        return {
            "project_result": {
                "score": 0,
                "depth_analysis": ["No projects found to analyze."],
                "suggestions": ["Please upload a resume containing project details."]
            }
        }
        
    try:
        # Load prompt template
        prompt_template = get_project_prompt_template()
        
        # Format parsed resume to pretty JSON string for context
        parsed_resume_str = json.dumps(parsed_resume, indent=2)
        
        # Initialize LLM with structured output configuration
        from app.parser.structured_parser import get_llm
        llm = get_llm(model_name="gemini-2.5-flash", temperature=0.0)
        structured_llm = llm.with_structured_output(ProjectAgentOutput)
        
        # Define chat prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior systems architect and technical lead evaluating resume projects."),
            ("user", prompt_template)
        ])
        
        # Create chain
        chain = prompt | structured_llm
        
        # Execute
        result: ProjectAgentOutput = chain.invoke({
            "raw_resume_text": raw_text,
            "parsed_resume": parsed_resume_str
        })
        
        logger.info("Project Depth Agent evaluation successfully complete.")
        return {"project_result": result.model_dump()}
        
    except Exception as e:
        logger.error(f"Error in Project Agent execution: {str(e)}")
        # Graceful fallback to prevent graph pipeline breakdown
        return {
            "project_result": {
                "score": 50,
                "depth_analysis": [f"Error occurred during project analysis: {str(e)}"],
                "suggestions": ["Retry the analysis or verify the Gemini API configuration."]
            }
        }
