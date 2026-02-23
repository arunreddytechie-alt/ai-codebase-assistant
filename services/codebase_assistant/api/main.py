from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from services.codebase_assistant.llm.llm_service import LLMService
from services.codebase_assistant.ingestion.ingest import ingest_github
from services.codebase_assistant.vectorstore.chroma_store import ChromaStore
from fastapi.responses import HTMLResponse
# =====================================
# INIT APP
# =====================================

app = FastAPI(
    title="AI Codebase Assistant",
    version="2.0",
    description="Ask questions about any GitHub repository (multi-repo supported)"
)


# Initialize services once (singleton)
llm_service = LLMService()

vector_store = ChromaStore()

# =====================================
# REQUEST MODELS
# =====================================

class RepoListResponse(BaseModel):
    repos: list[str]
    count: int

class QuestionRequest(BaseModel):
    repo_name: str
    question: str


class AnswerResponse(BaseModel):
    answer: str


class GitHubIngestRequest(BaseModel):
    github_url: str


class IngestResponse(BaseModel):
    status: str
    repo_name: str
    chunks_ingested: int
    message: str


# =====================================
# HEALTH CHECK
# =====================================

@app.get("/health")
def health():

    return {
        "status": "ok",
        "service": "AI Codebase Assistant",
        "multi_repo_support": True
    }


# =====================================
# GITHUB INGEST ENDPOINT
# =====================================

@app.post("/ingest/github", response_model=IngestResponse)
def ingest_github_repo(request: GitHubIngestRequest):

    try:

        github_url = request.github_url.strip()

        repo_name = github_url.rstrip("/").split("/")[-1]

        print(f"\nIngesting GitHub repo: {repo_name}")
        print(f"URL: {github_url}")

        chunks = ingest_github(github_url)

        print(f"Chunks ingested: {len(chunks)}")

        return IngestResponse(
            status="success",
            repo_name=repo_name,
            chunks_ingested=len(chunks),
            message=f"Repository '{repo_name}' ingested successfully"
        )

    except Exception as e:

        print(f"ERROR during ingestion: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =====================================
# ASK QUESTION ENDPOINT (MULTI-REPO)
# =====================================

@app.post("/ask", response_model=AnswerResponse)
def ask_question(request: QuestionRequest):

    try:

        repo_name = request.repo_name.strip()
        question = request.question.strip()

        print("\n===================================")
        print(f"Repo: {repo_name}")
        print(f"Question: {question}")
        print("===================================\n")

        answer = llm_service.ask(
            question=question,
            repo_name=repo_name
        )

        return AnswerResponse(answer=answer)

    except Exception as e:

        print(f"ERROR during question answering: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
# =====================================
# LIST ALL INGESTED REPOS
# =====================================

@app.get("/repos", response_model=RepoListResponse)
def list_repos():

    try:

        print("\nFetching list of repos from vector DB...")

        results = vector_store.collection.get()

        metadatas = results.get("metadatas", [])

        repo_set = set()

        for meta in metadatas:

            if meta and "repo_name" in meta:

                repo_set.add(meta["repo_name"])

        repos = sorted(list(repo_set))

        print(f"Found repos: {repos}")

        return RepoListResponse(
            repos=repos,
            count=len(repos)
        )

    except Exception as e:

        print(f"ERROR fetching repos: {str(e)}")

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
@app.get("/", response_class=HTMLResponse)
def ui():

    with open("services/codebase_assistant/ui/index.html") as f:
        return f.read()