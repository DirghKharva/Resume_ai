"""
graph package - LangGraph workflow definitions.

Responsible for:
    - Building the multi-agent state graph.
    - Defining edges and conditional routing.
    - Running the orchestration workflow.
"""

from app.graph.first_graph import first_graph
from app.graph.multi_agent_graph import multi_agent_graph
from app.graph.parallel_graph import parallel_graph

__all__ = [
    "first_graph",
    "multi_agent_graph",
    "parallel_graph",
]
