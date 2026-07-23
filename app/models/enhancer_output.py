from typing import List
from pydantic import BaseModel, Field


class TextEdit(BaseModel):
    """
    Represents a single atomic edit operation to apply to the resume DOCX file.

    The DOCX Editor agent iterates through a list of these and applies
    them one-by-one using the Office-Word-MCP-Server tools.
    """

    action: str = Field(
        description=(
            "The type of edit to perform. Must be one of:\n"
            "  'replace'       — Find target_text in the document and replace it with new_text.\n"
            "  'insert_after'  — Insert new_text as a new paragraph after the paragraph containing target_text.\n"
            "  'delete'        — Delete the paragraph containing target_text.\n"
            "  'append_bullet' — Append new_text as a new bullet point after the paragraph containing target_text."
        )
    )

    target_text: str = Field(
        description=(
            "The exact existing text in the document to locate the edit position. "
            "For 'replace': this is the text to be replaced. "
            "For 'insert_after'/'append_bullet': this is the anchor text to insert after. "
            "For 'delete': this is the text of the paragraph to remove. "
            "Keep this short and unique enough to identify the correct paragraph."
        )
    )

    new_text: str = Field(
        default="",
        description=(
            "The replacement or new content. "
            "For 'replace': the new text that replaces target_text. "
            "For 'insert_after': the new paragraph content to add. "
            "For 'append_bullet': the new bullet point text. "
            "For 'delete': leave this empty."
        )
    )

    section: str = Field(
        description=(
            "The resume section this edit belongs to. "
            "Examples: 'Skills', 'Experience', 'Projects', 'Summary', 'Education'."
        )
    )


class EnhancerPlan(BaseModel):
    """
    The complete enhancement plan produced by the Enhancement Agent.

    Contains an ordered list of TextEdit operations to apply to the original
    DOCX file, plus a human-readable changelog for the user.
    """

    edits: List[TextEdit] = Field(
        description=(
            "An ordered list of TextEdit operations to apply to the resume. "
            "Edits are applied in order, so place foundational changes (e.g., section rewrites) "
            "before dependent ones (e.g., bullet insertions within that section)."
        )
    )

    enhancements_made: List[str] = Field(
        description=(
            "A human-readable changelog of all improvements made. "
            "Each entry should be a concise one-liner. "
            "Example: 'Added Docker and Kubernetes to Skills section.' "
            "Example: 'Rewrote 3 Experience bullet points using STAR method.'"
        )
    )
