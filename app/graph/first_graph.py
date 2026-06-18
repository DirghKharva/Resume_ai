from langgraph.graph import StateGraph, START, END

from app.models.state import ResumeState
from app.agents.ats_agent import ats_agent

# Initialize the StateGraph with our ResumeState TypedDict
builder = StateGraph(ResumeState)

# Add the ATS Agent node
builder.add_node("ats_agent", ats_agent)

# Define the workflow connections
# START -> ats_agent -> END
builder.add_edge(START, "ats_agent")
builder.add_edge("ats_agent", END)

# Compile the graph into an executable Runnable
first_graph = builder.compile()
