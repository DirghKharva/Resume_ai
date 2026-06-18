import os
import json
import logging
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

from app.models.resume import ParsedResume
from app.prompts.parser_prompts import (
    RESUME_PARSER_SYSTEM_PROMPT,
    RESUME_PARSER_USER_PROMPT_TEMPLATE,
)

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def get_llm(model_name: str = "gemini-2.5-flash", temperature: float = 0.0) -> ChatGoogleGenerativeAI:
    """
    Helper function to initialize the Google Gemini LLM using langchain-google-genai.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is not set. Please set it in your environment or .env file."
        )
    
    return ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=api_key,
    )

def parse_raw_resume_to_structured(
    raw_text: str,
    model_name: str = "gemini-2.5-flash"
) -> Dict[str, Any]:
    """
    Uses Gemini API and LangChain structured outputs to parse raw resume text
    into a structured JSON/dictionary matching ParsedResume.
    
    Args:
        raw_text (str): The raw text extracted from the resume file.
        model_name (str): The Gemini model to use. Defaults to 'gemini-1.5-flash'.
        
    Returns:
        dict: The structured resume data matching ParsedResume schema.
    """
    if not raw_text.strip():
        logger.warning("Empty raw resume text passed to structured parser.")
        return ParsedResume(
            name="Unknown Candidate",
            skills=[],
            education=[],
            experience=[],
            projects=[],
            certifications=[]
        ).model_dump()

    try:
        llm = get_llm(model_name=model_name, temperature=0.0)
        
        # Configure the LLM to output structured data matching ParsedResume
        structured_llm = llm.with_structured_output(ParsedResume)
        
        # Build prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", RESUME_PARSER_SYSTEM_PROMPT),
            ("user", RESUME_PARSER_USER_PROMPT_TEMPLATE)
        ])
        
        # Create chain and execute
        chain = prompt | structured_llm
        logger.info(f"Invoking LLM ({model_name}) for structured resume parsing...")
        result = chain.invoke({"raw_text": raw_text})
        
        # result is a ParsedResume instance, serialize it to dictionary
        return result.model_dump()
        
    except Exception as e:
        logger.error(f"Error during structured resume parsing: {str(e)}")
        # Fallback empty structured result to avoid breaking the graph flow
        return ParsedResume(
            name="Error Parsing Name",
            skills=[],
            education=[],
            experience=[],
            projects=[],
            certifications=[]
        ).model_dump()
