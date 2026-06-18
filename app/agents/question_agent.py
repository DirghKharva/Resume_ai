import json
import logging
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate

from app.models.state import ResumeState
from app.models.agent_outputs import QuestionAgentOutput
from app.prompts import get_question_prompt_template

logger = logging.getLogger(__name__)

def question_agent(state: ResumeState) -> Dict[str, Any]:
    """
    Question Agent Node. Evaluates the resume to generate intelligent follow-up
    questions to probe deeper into candidate projects/roles.
    
    Args:
        state (ResumeState): The current LangGraph state.
        
    Returns:
        dict: A dictionary updating the state with 'question_result'.
    """
    logger.info("Question Agent processing resume...")
    raw_text = state.get("raw_resume_text", "")
    parsed_resume = state.get("parsed_resume", {})
    
    if not raw_text.strip():
        logger.warning("No raw resume text provided to Question Agent.")
        return {
            "question_result": {
                "questions": ["Please upload a valid resume to generate questions."]
            }
        }
        
    try:
        # Load prompt template
        prompt_template = get_question_prompt_template()
        
        # Format parsed resume to pretty JSON string for context
        parsed_resume_str = json.dumps(parsed_resume, indent=2)
        
        # Initialize LLM with structured output configuration
        from app.parser.structured_parser import get_llm
        llm = get_llm(model_name="gemini-2.5-flash", temperature=0.0)
        structured_llm = llm.with_structured_output(QuestionAgentOutput)
        
        # Define chat prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a technical interviewer who digs deep into projects and experience."),
            ("user", prompt_template)
        ])
        
        # Create chain
        chain = prompt | structured_llm
        
        # Execute
        result: QuestionAgentOutput = chain.invoke({
            "raw_resume_text": raw_text,
            "parsed_resume": parsed_resume_str
        })
        
        logger.info("Question Agent successfully generated questions.")
        return {"question_result": result.model_dump()}
        
    except Exception as e:
        logger.error(f"Error in Question Agent execution: {str(e)}")
        # Graceful fallback to prevent graph pipeline breakdown
        return {
            "question_result": {
                "questions": [
                    "Which technologies and architectures were used in your main project?",
                    "What were the key quantitative results or business metrics achieved?",
                    "What was your individual contribution to the team's outcomes?"
                ]
            }
        }
