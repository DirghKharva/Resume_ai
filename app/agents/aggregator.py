import json
import logging
from typing import Dict, Any

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.models.state import ResumeState
from app.models.agent_outputs import AggregatedResultOutput
from app.prompts import get_aggregator_prompt_template

logger = logging.getLogger(__name__)

class AggregatorLLMOutput(BaseModel):
    """Temporary structured output for the LLM synthesis part of the Aggregator."""
    priority_fixes: list[str] = Field(default_factory=list)
    dashboard_data: dict[str, Any] = Field(default_factory=dict)

def aggregator(state: ResumeState) -> Dict[str, Any]:
    """
    Aggregator Node. Programmatically calculates the overall score and uses
    Gemini structured output to compile priority fixes and dashboard structure.
    
    Args:
        state (ResumeState): The current LangGraph state.
        
    Returns:
        dict: A dictionary updating the state with 'aggregated_result'.
    """
    logger.info("Aggregator Node synthesizing agent outputs...")
    
    # Extract agent results
    ats = state.get("ats_result", {})
    recruiter = state.get("recruiter_result", {})
    grammar = state.get("grammar_result", {})
    project = state.get("project_result", {})
    keyword = state.get("keyword_result", {})
    
    # 1. Programmatic Overall Score Calculation
    # Extract scores with default fallbacks
    ats_score = ats.get("score", 70)
    recruiter_score = recruiter.get("shortlist_probability", 70)
    keyword_score = keyword.get("match_score", 70)
    grammar_score = grammar.get("score", 70)
    
    if project and "score" in project:
        # If Project agent result is present
        project_score = project.get("score", 70)
        overall_score = int(
            (ats_score * 0.25) +
            (recruiter_score * 0.25) +
            (keyword_score * 0.20) +
            (project_score * 0.15) +
            (grammar_score * 0.15)
        )
    else:
        # Standard calculation without Project agent
        overall_score = int(
            (ats_score * 0.30) +
            (recruiter_score * 0.30) +
            (keyword_score * 0.25) +
            (grammar_score * 0.15)
        )
        
    logger.info(f"Programmatically computed overall score: {overall_score}")
    
    # 2. LLM Synthesis for Priority Fixes and Dashboard Statuses
    try:
        # Load prompt template
        prompt_template = get_aggregator_prompt_template()
        
        # Format results into pretty JSON strings
        ats_str = json.dumps(ats, indent=2)
        recruiter_str = json.dumps(recruiter, indent=2)
        grammar_str = json.dumps(grammar, indent=2)
        project_str = json.dumps(project, indent=2) if project else "Not analyzed"
        keyword_str = json.dumps(keyword, indent=2)
        
        # Initialize LLM with structured output configuration
        from app.parser.structured_parser import get_llm
        llm = get_llm(model_name="gemini-2.5-flash", temperature=0.0)
        structured_llm = llm.with_structured_output(AggregatorLLMOutput)
        
        # Define chat prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a senior resume aggregation and talent acquisition coordinator."),
            ("user", prompt_template)
        ])
        
        # Create chain
        chain = prompt | structured_llm
        
        # Execute
        result: AggregatorLLMOutput = chain.invoke({
            "ats_result": ats_str,
            "recruiter_result": recruiter_str,
            "grammar_result": grammar_str,
            "project_result": project_str,
            "keyword_result": keyword_str
        })
        
        # Merge programmatic score with LLM output
        final_result = AggregatedResultOutput(
            overall_score=overall_score,
            priority_fixes=result.priority_fixes,
            dashboard_data=result.dashboard_data
        )
        
        logger.info("Aggregator synthesis successfully complete.")
        return {"aggregated_result": final_result.model_dump()}
        
    except Exception as e:
        logger.error(f"Error in Aggregator execution: {str(e)}")
        # Construct fallback representation
        fallback_fixes = []
        if ats.get("issues"):
            fallback_fixes.append(f"ATS Issue: {ats['issues'][0]}")
        if keyword.get("missing_skills"):
            fallback_fixes.append(f"Keyword Gap: Missing {keyword['missing_skills'][0]}")
        if grammar.get("errors"):
            fallback_fixes.append(f"Grammar Issue: {grammar['errors'][0]}")
            
        if not fallback_fixes:
            fallback_fixes = ["Review formatting and structure.", "Add missing target skills."]
            
        fallback_dashboard = {
            "ats_status": "Checked",
            "recruiter_status": "Checked",
            "grammar_status": "Checked",
            "keyword_status": "Checked",
            "category_scores": {
                "ats": ats_score,
                "recruiter": recruiter_score,
                "grammar": grammar_score,
                "keyword": keyword_score
            }
        }
        
        return {
            "aggregated_result": {
                "overall_score": overall_score,
                "priority_fixes": fallback_fixes,
                "dashboard_data": fallback_dashboard
            }
        }
