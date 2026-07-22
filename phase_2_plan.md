# Phase 2 Plan: Resume Enhancement Engine

This document outlines the architecture, technical components, and implementation plan for **Phase 2** of the JobCopilot AI resume analysis system.

---

## 🎯 Goal

Phase 2 takes the Phase 1 analysis report + the user's answers to AI-generated follow-up questions, and **directly edits the original uploaded `.docx` resume file** — preserving its original formatting, fonts, and layout — to produce a polished, role-optimized resume.

---

## 🔁 End-to-End Flow

```
Phase 1 Analysis Complete
         │
         ▼
User answers follow-up questions (in Streamlit UI)
         │
         ▼
POST /api/v1/enhance
         │
         ├──► Enhancement Agent (LLM)
         │       Reads: parsed_resume + all Phase 1 agent results + user answers
         │       Outputs: EnhancerPlan (list of structured TextEdit operations)
         │
         └──► DOCX Editor Node
                 Calls Office-Word-MCP-Server tools to apply edits:
                 - search_and_replace(old_text, new_text)
                 - insert_paragraph(after=target, new_text=content)
                 - delete_paragraph(index)
                 - append_bullet(text, after=target)
         │
         ▼
outputs/enhanced_{filename}.docx  ←  formatting preserved, content improved
         │
         ▼
Streamlit: Changelog + Download Button
```

---

## 🧩 Components to Build

### 1. Pydantic Models (`app/models/enhancer_output.py`)

Two new schemas:

* **`TextEdit`**: Represents a single atomic edit operation.
  * `action`: One of `"replace"`, `"insert_after"`, `"delete"`, `"append_bullet"`
  * `target_text`: Existing text in the document to locate the edit position.
  * `new_text`: The replacement or new content to insert.
  * `section`: Section context (e.g., `"Skills"`, `"Experience"`, `"Projects"`).

* **`EnhancerPlan`**: The full enhancement output from the LLM.
  * `edits: List[TextEdit]` — ordered list of all edits to apply.
  * `enhancements_made: List[str]` — human-readable changelog.

---

### 2. Enhancement Prompt (`app/prompts/enhancer_prompt.txt`)

The prompt instructs the LLM to:
* Review all Phase 1 agent feedback (ATS issues, missing keywords, grammar errors, project depth, recruiter impressions).
* Incorporate the user's answers into experience and project bullet points.
* Add missing skills and keywords from the Keyword Agent's gap list.
* Rewrite weak bullet points using the **STAR method** (Situation, Task, Action, Result).
* Fix every grammar error reported by the Grammar Agent.
* Output a clean, structured `EnhancerPlan` JSON (NOT prose).

---

### 3. Enhancement Agent (`app/agents/enhancer_agent.py`)

* Reads the `enhancer_prompt.txt` template.
* Calls `get_llm()` — supports both Gemini and Ollama.
* Uses `llm.with_structured_output(EnhancerPlan)` to enforce structured output.
* Returns the `EnhancerPlan` to the LangGraph state.

---

### 4. DOCX Editor Node (`app/agents/docx_editor.py`)

* Integrates with the **[Office-Word-MCP-Server](https://github.com/GongRzhe/Office-Word-MCP-Server)** using `langchain-mcp-adapters`.
* Iterates through each `TextEdit` in the `EnhancerPlan`.
* Applies edits to the original `.docx` file using MCP tool calls.
* Saves the result as `outputs/enhanced_{original_filename}.docx`.

> **Why Office-Word-MCP-Server?**
> It operates directly on the Word XML structure, preserving all fonts, colors,
> column layouts, tables, and section formatting. Unlike raw `python-docx`,
> it handles complex designer templates correctly.

---

### 5. Enhancement Graph (`app/graph/enhancement_graph.py`)

Simple 2-node sequential LangGraph:
```
START → Enhancement Agent → DOCX Editor Node → END
```
Sequential execution is intentional — the editor must wait for the `EnhancerPlan` before applying edits.

---

### 6. API Endpoint (`app/api/resume.py`)

**Update `/analyze`:**
* Stop deleting the uploaded file after analysis.
* Return the `resume_path` in the response payload so it can be passed to `/enhance`.
* Add a `DELETE /api/v1/cleanup/{filename}` endpoint for manual cleanup.

**New `POST /api/v1/enhance`:**
* Request Body (JSON):
  * `resume_path` — path of the saved original `.docx` file
  * `parsed_resume` — structured resume dictionary from Phase 1
  * `user_answers` — `{question: answer}` mapping
  * `target_role`, `job_description`
  * `ats_result`, `recruiter_result`, `grammar_result`, `project_result`, `keyword_result`
* Response:
  * `enhanced_file_path` — path to the new enhanced `.docx` file
  * `enhancements_made` — list of human-readable changelog entries

---

### 7. Streamlit UI (`app.py`)

Update the **Interview Prep** tab:
* Display each question with a `st.text_area()` input field for user answers.
* Add a **✨ Generate Enhanced Resume** button.
* On click, POST to `/api/v1/enhance`.
* On success, display:
  * **📋 Enhancements Changelog** — expandable list of changes.
  * **⬇️ Download Enhanced Resume** — Streamlit download button for the `.docx`.

---

## 📦 Dependencies to Add

| Package | Purpose |
|---|---|
| `langchain-mcp-adapters` | Bridge between LangGraph and MCP tool servers |
| `office-word-mcp-server` | DOCX editing while preserving formatting |

---

## ⚠️ Constraints & Known Limitations

| Scenario | Behavior |
|---|---|
| User uploaded **DOCX** | ✅ Full in-place editing with formatting preserved |
| User uploaded **PDF** | ❌ Cannot edit PDF. UI will prompt user to re-upload as DOCX |
| Complex multi-column templates | ✅ MCP-Server handles column layouts correctly |
| Custom embedded fonts | ⚠️ Fonts preserved only if installed on the system |

---

## ✅ Testing Plan

* **`tests/test_enhancer.py`**: Mock LLM + mock MCP tools, verify `EnhancerPlan` schema and correct edit operations are generated.
* **`tests/test_docx_editor.py`**: Verify edit operations are correctly applied to a sample `.docx` test fixture.
* **Manual verification**: Download and open the enhanced `.docx` — confirm keywords added, bullet points rewritten, and original layout preserved.

---

## 🗺️ Revised Project Roadmap

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Multi-Agent Resume Analyzer — generates full analysis report | ✅ Complete |
| Phase 2 | Resume Enhancement Engine — AI edits original DOCX preserving layout | 🔜 In Progress |
