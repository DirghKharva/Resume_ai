"""
Phase 2 Enhancement Graph — Resume Enhancement Engine.

This module implements a LangGraph workflow that:
1. Makes a safe copy of the original resume
2. Launches the Office-Word-MCP-Server as a stdio subprocess
3. Loads ALL 30+ Word document tools via langchain-mcp-adapters
4. Runs a LangGraph ReAct agent that autonomously edits the resume copy
   using whichever MCP tools it decides are most appropriate

The LLM agent reads the Phase 1 analysis + user answers and applies
targeted edits directly to the .docx file, preserving original formatting.
"""

import os
import sys
import shutil
import logging
import asyncio
from pathlib import Path
from typing import Any, Dict

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools

from app.models.state import ResumeState

logger = logging.getLogger(__name__)

# Path to the cloned Office-Word-MCP-Server entry point
MCP_SERVER_SCRIPT = str(
    Path(__file__).resolve().parent.parent.parent
    / "Office-Word-MCP-Server"
    / "word_mcp_server.py"
)

# Path to the prompts directory
PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "enhancer_prompt.txt"


def get_llm():
    """
    Return the configured LLM (supports both Gemini and Ollama).
    Reads OLLAMA_MODEL and GEMINI_API_KEY from environment.
    """
    ollama_model = os.getenv("OLLAMA_MODEL")
    gemini_key = os.getenv("GEMINI_API_KEY")

    if ollama_model:
        from langchain_ollama import ChatOllama
        logger.info(f"Enhancement Agent using Ollama model: {ollama_model}")
        return ChatOllama(model=ollama_model, temperature=0)
    elif gemini_key:
        from langchain_google_genai import ChatGoogleGenerativeAI
        logger.info("Enhancement Agent using Gemini.")
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=gemini_key,
            temperature=0,
        )
    else:
        raise ValueError(
            "No LLM configured. Set OLLAMA_MODEL or GEMINI_API_KEY in your .env file."
        )


def _make_enhanced_copy(original_path: str) -> str:
    """
    Create a copy of the original resume to edit.
    Returns the path to the new copy.

    Example:
        uploads/resume.docx → outputs/enhanced_resume.docx
    """
    original = Path(original_path)
    outputs_dir = original.parent.parent / "outputs"
    outputs_dir.mkdir(exist_ok=True)

    enhanced_path = outputs_dir / f"enhanced_{original.name}"
    shutil.copy2(original_path, str(enhanced_path))
    logger.info(f"Created enhanced copy at: {enhanced_path}")
    return str(enhanced_path)


def _build_prompt(state: ResumeState, doc_path: str) -> str:
    """
    Load the enhancer prompt template and fill in all placeholders
    from the Phase 1 analysis results and user answers.
    """
    with open(PROMPT_PATH, "r") as f:
        template = f.read()

    # Format user answers as readable Q&A pairs
    user_answers = state.get("user_answers", {})
    if user_answers:
        qa_lines = [f"Q: {q}\nA: {a}" for q, a in user_answers.items()]
        answers_text = "\n\n".join(qa_lines)
    else:
        answers_text = "No answers provided."

    return template.format(
        doc_path=doc_path,
        target_role=state.get("target_role", "Not specified"),
        job_description=state.get("job_description", "Not provided"),
        ats_result=state.get("ats_result", {}),
        recruiter_result=state.get("recruiter_result", {}),
        grammar_result=state.get("grammar_result", {}),
        project_result=state.get("project_result", {}),
        keyword_result=state.get("keyword_result", {}),
        user_answers=answers_text,
    )


async def run_enhancement_graph(state: ResumeState) -> Dict[str, Any]:
    """
    Main entry point for Phase 2 enhancement.

    Steps:
    1. Copy the original resume to outputs/enhanced_{filename}.docx
    2. Start the Office-Word-MCP-Server as a stdio subprocess
    3. Load all MCP Word tools via langchain-mcp-adapters
    4. Create a ReAct agent with those tools
    5. Run the agent with the filled-in enhancement prompt
    6. Return the path to the enhanced file + the agent's summary

    Args:
        state: The ResumeState dict containing Phase 1 results and user answers

    Returns:
        dict with keys:
            - enhanced_file_path: path to the enhanced .docx
            - enhancements_made: list of improvement summaries
            - agent_log: full agent message history for display
    """
    resume_path = state.get("resume_path", "")

    # Only DOCX files can be edited in-place
    if not resume_path.lower().endswith(".docx"):
        return {
            "enhanced_file_path": None,
            "enhancements_made": [],
            "error": "Enhancement requires a .docx file. Please re-upload your resume as a Word document.",
        }

    # Step 1: Create a safe copy so we never touch the original
    doc_path = _make_enhanced_copy(resume_path)

    # Step 2: Build the enhancement prompt
    prompt = _build_prompt(state, doc_path)

    # Step 3: Get the LLM
    llm = get_llm()

    # Step 4: Start MCP server and load tools
    logger.info(f"Starting Office-Word-MCP-Server from: {MCP_SERVER_SCRIPT}")

    server_params = StdioServerParameters(
        command=sys.executable,          # Use the current Python interpreter (from myenv)
        args=[MCP_SERVER_SCRIPT],        # Run the word_mcp_server.py script
        env={
            **os.environ,
            "PYTHONPATH": str(           # Make sure word_document_server package is found
                Path(MCP_SERVER_SCRIPT).parent
            ),
        },
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP connection
            await session.initialize()
            logger.info("MCP session initialized.")

            # Load all available Word document tools
            tools = await load_mcp_tools(session)
            logger.info(f"Loaded {len(tools)} MCP tools: {[t.name for t in tools]}")

            # Step 5: Create the ReAct agent with MCP tools
            agent = create_react_agent(llm, tools)

            # Step 6: Run the agent
            messages = [HumanMessage(content=prompt)]
            result = await agent.ainvoke({"messages": messages})

    # Extract the agent's final message
    final_message = result["messages"][-1].content if result.get("messages") else ""

    # Parse the enhancements list from the agent's output
    enhancements = []
    if "ENHANCEMENTS MADE:" in final_message:
        section = final_message.split("ENHANCEMENTS MADE:")[-1].strip()
        enhancements = [
            line.lstrip("- ").strip()
            for line in section.splitlines()
            if line.strip().startswith("-")
        ]

    logger.info(f"Enhancement complete. {len(enhancements)} improvements made.")

    return {
        "enhanced_file_path": doc_path,
        "enhancements_made": enhancements,
        "agent_log": [m.content for m in result.get("messages", [])],
    }


def enhance_resume(state: ResumeState) -> Dict[str, Any]:
    """
    Synchronous wrapper around run_enhancement_graph.
    Called from the FastAPI endpoint (which uses asyncio.run or runs in event loop).
    """
    return asyncio.run(run_enhancement_graph(state))
