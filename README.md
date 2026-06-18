# JobCopilot AI — Resume Analyzer

> **Phase 1** of a multi-phase AI-powered career assistant.  
> Analyzes resumes using six specialized AI agents built with LangGraph and Gemini.

---

## Project Structure

```
resume-ai/
├── app/
│   ├── agents/     # Six specialized AI agents
│   ├── graph/      # LangGraph workflow orchestration
│   ├── parser/     # PDF and DOCX resume parsing
│   ├── models/     # Pydantic data models & schemas
│   ├── prompts/    # LLM prompt templates
│   └── api/        # FastAPI route definitions
├── uploads/        # Uploaded resume files (gitignored)
├── outputs/        # Generated analysis results (gitignored)
├── tests/          # Unit and integration tests
├── main.py         # Application entry point
├── requirements.txt
└── .env.example    # Environment variable template
```

---

## Agents

| Agent | Responsibility |
|---|---|
| **ATS Agent** | ATS compatibility, formatting, structure |
| **Recruiter Agent** | First impression, shortlisting probability |
| **Grammar Agent** | Grammar, readability, sentence quality |
| **Project Agent** | Technical depth, metrics, impact |
| **Keyword Agent** | Missing skills, keyword gaps |
| **Question Agent** | Intelligent follow-up questions |

---

## Tech Stack

- **Backend**: FastAPI
- **Agent Framework**: LangGraph
- **LLM**: Google Gemini API
- **Parsing**: pdfplumber, python-docx
- **Frontend**: Streamlit (Phase 1)
- **Validation**: Pydantic v2

---

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Linux/macOS
   venv\Scripts\activate           # Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   ```bash
   cp .env.example .env
   # Add your GOOGLE_API_KEY to .env
   ```

4. Run the server:
   ```bash
   python main.py
   ```

   API available at: `http://localhost:8000`  
   Docs at: `http://localhost:8000/docs`

---

## Roadmap

- [x] Phase 1 — Multi-Agent Resume Analyzer *(current)*
- [ ] Phase 2 — Resume Enhancement Engine
- [ ] Phase 3 — Job Matching Engine
- [ ] Phase 4 — Cold Email Generator
- [ ] Phase 5 — Application Automation
