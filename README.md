# AI Codebase Assistant

AI Codebase Assistant is an AI-powered system that understands entire codebases and answers questions about them.

It works like a lightweight GitHub Copilot for full repository understanding using semantic search, dependency graph expansion, and LLM reasoning.

You can ingest any GitHub repository and ask architecture, implementation, or functionality questions.

---

# Features

- Ingest any GitHub repository
- Supports multiple repositories
- Semantic search across entire codebase
- Dependency-aware retrieval using code graph
- Repo-isolated search
- Architecture-aware answers
- FastAPI backend
- Local vector database (ChromaDB)
- OpenAI powered reasoning

Run this command on termnial

PYTHONPATH=. uvicorn services.codebase_assistant.api.main:app --reload --reload-exclude "data/*"
