import os
from openai import OpenAI
from dotenv import load_dotenv

from services.codebase_assistant.retrieval.intent_router import IntentRouter
from services.codebase_assistant.retrieval.hybrid_retriever import HybridRetriever


# =====================================
# LOAD ENV VARIABLES
# =====================================

load_dotenv()


# =====================================
# LLM SERVICE
# =====================================

class LLMService:

    def __init__(self):

        print("Initializing LLM Service...")

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.retriever = HybridRetriever()

        self.intent_router = IntentRouter()

        print("LLM Service ready")


    # =====================================
    # MAIN ENTRYPOINT
    # =====================================

    def ask(self, question: str, repo_name: str):

        print("\n===================================")
        print(f"Repo: {repo_name}")
        print(f"Question: {question}")
        print("===================================")

        # STEP 1: Detect intent
        intent = self.intent_router.detect_intent(question)

        print(f"Detected intent: {intent}")


        # =====================================
        # STEP 2: API INTENT → USE STRUCTURED SUMMARY
        # =====================================

        if intent == "api":

            api_summary = self._build_api_summary(repo_name)

            if api_summary:

                prompt = f"""
You are a senior backend architect.

Use the API SUMMARY below to answer the question.

API SUMMARY:
{api_summary}

QUESTION:
{question}

Instructions:
- List APIs clearly
- Include HTTP method and path
- Do NOT hallucinate

ANSWER:
"""

                return self._call_llm(prompt)

            else:
                print("No API metadata found, falling back to retrieval")


        # =====================================
        # STEP 3: RETRIEVE CHUNKS
        # =====================================

        chunks = self.retriever.retrieve(
            query=question,
            repo_name=repo_name,
            intent=intent
        )

        print(f"Chunks retrieved: {len(chunks)}")

        if not chunks:
            return "No relevant information found in this repository."


        # =====================================
        # STEP 4: BUILD CONTEXT
        # =====================================

        context = self._build_context(chunks, repo_name)

        print("\nContext preview:")
        print(context[:500])


        # =====================================
        # STEP 5: BUILD PROMPT
        # =====================================

        prompt = self._build_prompt(question, context)


        # STEP 6: CALL LLM
        return self._call_llm(prompt)


    # =====================================
    # CALL OPENAI
    # =====================================

    def _call_llm(self, prompt: str):

        response = self.client.chat.completions.create(

            model="gpt-4o-mini",

            temperature=0,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior software architect.\n"
                        "Answer ONLY using provided information.\n"
                        "Do NOT hallucinate."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content.strip()


    # =====================================
    # BUILD CONTEXT
    # =====================================

    def _build_context(self, chunks, repo_name):

        results = self.retriever.vector_store.collection.get()

        metas = results.get("metadatas", [])

        context_parts = []


        # STEP 1: ADD API SUMMARY

        api_lines = []

        for meta in metas:

            if meta.get("repo_name") != repo_name:
                continue

            routes = meta.get("api_routes")

            if routes and isinstance(routes, list):

                for route in routes:

                    method = route.get("method")
                    path = route.get("path")

                    if method and path:
                        api_lines.append(f"{method} {path}")


        if api_lines:

            context_parts.append("API ENDPOINT SUMMARY:")
            context_parts.append("\n".join(sorted(set(api_lines))))
            context_parts.append("\n")


        # STEP 2: ADD CODE

        context_parts.append("RELEVANT CODE:")
        context_parts.append("\n\n".join(chunks[:10]))

        return "\n".join(context_parts)


    # =====================================
    # BUILD PROMPT
    # =====================================

    def _build_prompt(self, question, context):

        return f"""
You are analyzing a software codebase.

Use ONLY the provided context.

Rules:

If question is about APIs:
- List HTTP method
- List endpoint path
- List handler function if present

If question is about architecture:
- Explain structure clearly

If question is about setup:
- Explain setup steps clearly

DO NOT hallucinate.

CODEBASE CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""


    # =====================================
    # BUILD API SUMMARY (FIXED)
    # =====================================

    def _build_api_summary(self, repo_name: str):

        results = self.retriever.vector_store.collection.get()

        metas = results.get("metadatas", [])

        api_set = set()

        for meta in metas:

            if meta.get("repo_name") != repo_name:
                continue

            routes = meta.get("api_routes")

            if routes and isinstance(routes, list):

                for route in routes:

                    method = route.get("method")
                    path = route.get("path")

                    if method and path:
                        api_set.add(f"{method} {path}")


        if not api_set:
            return None


        api_list = sorted(api_set)

        summary = f"Total APIs: {len(api_list)}\n\n"

        summary += "API Endpoints:\n"

        for api in api_list:
            summary += f"- {api}\n"

        return summary