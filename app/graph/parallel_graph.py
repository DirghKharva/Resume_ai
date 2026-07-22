import logging
from typing import Dict, Any
from langgraph.graph import StateGraph, START, END

from app.models.state import ResumeState
from app.agents import (
    ats_agent,
    recruiter_agent,
    grammar_agent,
    project_agent,
    keyword_agent,
    question_agent,
    aggregator,
)

logger = logging.getLogger(__name__)

def parser_node(state: ResumeState) -> Dict[str, Any]:
    """
    Parser Node inside the LangGraph.
    Extracts raw text from pdf/docx if resume_path is provided, and then
    parses the raw text into structured JSON.
    """
    logger.info("Parser Node started.")
    raw_text = state.get("raw_resume_text", "")
    parsed_resume = state.get("parsed_resume", {})
    resume_path = state.get("resume_path", "")
    
    # 1. Extract raw text if path is provided but text is empty
    if not raw_text.strip() and resume_path:
        logger.info(f"Extracting text from: {resume_path}")
        try:
            from app.parser import parse_resume
            raw_text = parse_resume(resume_path)
        except ValueError as ve:
            logger.warning(str(ve))
        except Exception as e:
            logger.error(f"Error parsing resume: {str(e)}")
            
    # 2. Parse structured resume if raw text is available but JSON is empty
    if raw_text.strip() and not parsed_resume:
        logger.info("Parsing raw text to structured representation...")
        from app.parser.structured_parser import parse_raw_resume_to_structured
        parsed_resume = parse_raw_resume_to_structured(raw_text)
        
    logger.info("Parser Node successfully complete.")
    return {
        "raw_resume_text": raw_text,
        "parsed_resume": parsed_resume
    }

# Initialize StateGraph
builder = StateGraph(ResumeState)

# Add all nodes
builder.add_node("parser_node", parser_node)
builder.add_node("ats_agent", ats_agent)
builder.add_node("recruiter_agent", recruiter_agent)
builder.add_node("grammar_agent", grammar_agent)
builder.add_node("project_agent", project_agent)
builder.add_node("keyword_agent", keyword_agent)
builder.add_node("question_agent", question_agent)
builder.add_node("aggregator", aggregator)

# Define execution flow
# START -> Parser Node
builder.add_edge(START, "parser_node")

# Parallel fan-out from Parser Node to all 6 agents
builder.add_edge("parser_node", "ats_agent")
builder.add_edge("parser_node", "recruiter_agent")
builder.add_edge("parser_node", "grammar_agent")
builder.add_edge("parser_node", "project_agent")
builder.add_edge("parser_node", "keyword_agent")
builder.add_edge("parser_node", "question_agent")

# Parallel fan-in from all 6 agents converging to Aggregator
builder.add_edge("ats_agent", "aggregator")
builder.add_edge("recruiter_agent", "aggregator")
builder.add_edge("grammar_agent", "aggregator")
builder.add_edge("project_agent", "aggregator")
builder.add_edge("keyword_agent", "aggregator")
builder.add_edge("question_agent", "aggregator")

# Aggregator -> END
builder.add_edge("aggregator", END)

# Compile into runnable graph workflow
parallel_graph = builder.compile()
