from langgraph.graph import StateGraph, START, END

from app.models.state import ResumeState
from app.agents import (
    ats_agent,
    recruiter_agent,
    grammar_agent,
    keyword_agent,
    question_agent,
    aggregator,
)

# Initialize the StateGraph with our ResumeState TypedDict
builder = StateGraph(ResumeState)

# 1. Add all Agent and Aggregator nodes
builder.add_node("ats_agent", ats_agent)
builder.add_node("recruiter_agent", recruiter_agent)
builder.add_node("grammar_agent", grammar_agent)
builder.add_node("keyword_agent", keyword_agent)
builder.add_node("question_agent", question_agent)
builder.add_node("aggregator", aggregator)

# 2. Define parallel fan-out from START to all specialized agents
builder.add_edge(START, "ats_agent")
builder.add_edge(START, "recruiter_agent")
builder.add_edge(START, "grammar_agent")
builder.add_edge(START, "keyword_agent")
builder.add_edge(START, "question_agent")

# 3. Define fan-in from all specialized agents converging to the Aggregator
builder.add_edge("ats_agent", "aggregator")
builder.add_edge("recruiter_agent", "aggregator")
builder.add_edge("grammar_agent", "aggregator")
builder.add_edge("keyword_agent", "aggregator")
builder.add_edge("question_agent", "aggregator")

# 4. Connect Aggregator to END
builder.add_edge("aggregator", END)

# Compile the graph into an executable Runnable workflow
multi_agent_graph = builder.compile()
