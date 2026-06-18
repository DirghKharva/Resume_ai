import json
import logging
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate

from app.models.state import ResumeState
from app.models.agent_outputs import GrammarAgentOutput
from app.prompts import get_grammar_prompt_template

logger = logging.getLogger(__name__)

def grammar_agent(state: ResumeState) -> Dict[str, Any]:
    """
    Grammar Agent Node. Evaluates the resume for language quality, spelling,
    grammar, tense consistency, and readability.
    
    Args:
        state (ResumeState): The current LangGraph state.
        
    Returns:
        dict: A dictionary updating the state with 'grammar_result'.
    """
    logger.info("Grammar Agent processing resume...")
    raw_text = state.get("raw_resume_text", "")
    parsed_resume = state.get("parsed_resume", {})
    
    if not raw_text.strip():
        logger.warning("No raw resume text provided to Grammar Agent.")
        return {
            "grammar_result": {
                "score": 0,
                "errors": ["No resume content found to analyze."],
                "suggestions": ["Please upload a valid resume."]
            }
        }
        
    try:
        # Load prompt template
        prompt_template = get_grammar_prompt_template()
        
        # Format parsed resume to pretty JSON string for context
        parsed_resume_str = json.dumps(parsed_resume, indent=2)
        
        # Initialize LLM with structured output configuration
        from app.parser.structured_parser import get_llm
        llm = get_llm(model_name="gemini-2.5-flash", temperature=0.0)
        structured_llm = llm.with_structured_output(GrammarAgentOutput)
        
        # Define chat prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a specialized AI editor focused on professional resume copyediting."),
            ("user", prompt_template)
        ])
        
        # Create chain
        chain = prompt | structured_llm
        
        # Execute
        result: GrammarAgentOutput = chain.invoke({
            "raw_resume_text": raw_text,
            "parsed_resume": parsed_resume_str
        })
        
        logger.info("Grammar Agent evaluation successfully complete.")
        return {"grammar_result": result.model_dump()}
        
    except Exception as e:
        logger.error(f"Error in Grammar Agent execution: {str(e)}")
        # Graceful fallback to prevent graph pipeline breakdown
        return {
            "grammar_result": {
                "score": 50,
                "errors": [f"Error occurred during grammar analysis: {str(e)}"],
                "suggestions": ["Retry the analysis or verify the Gemini API configuration."]
            }
        }
