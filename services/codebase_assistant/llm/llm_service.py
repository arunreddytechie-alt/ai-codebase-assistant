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

        # Hybrid retriever
        self.retriever = HybridRetriever()

        # Intent router
        self.intent_router = IntentRouter()

        print("LLM Service ready")


    # =====================================
    # MAIN ENTRYPOINT
    # =====================================

    def ask(self, question: str, repo_name: str):

        print(f"\n===================================")
        print(f"Repo: {repo_name}")
        print(f"Question: {question}")
        print(f"===================================")

        # =====================================
        # STEP 1: DETECT INTENT
        # =====================================

        intent = self.intent_router.detect_intent(question)

        print(f"Detected intent: {intent}")


        # =====================================
        # STEP 2: SPECIAL HANDLING FOR API INTENT
        # =====================================

        if intent == "api":

            api_summary = self._build_api_summary(repo_name)

            if api_summary:

                prompt = f"""
You are an expert backend architect.

Use the API SUMMARY below to answer the question.

API SUMMARY:
{api_summary}

QUESTION:
{question}

ANSWER clearly and technically:
"""

                return self._call_llm(prompt)

            else:
                print("No structured API metadata found, falling back to retrieval")


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

        context = self._build_context(chunks)

        print("\nContext preview:")
        print(context[:500])


        # =====================================
        # STEP 5: BUILD PROMPT
        # =====================================

        prompt = self._build_prompt(question, context)


        # =====================================
        # STEP 6: CALL OPENAI
        # =====================================

        return self._call_llm(prompt)


    # =====================================
    # CALL OPENAI
    # =====================================

    def _call_llm(self, prompt: str):

        response = self.client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a senior software architect.\n"
                        "Answer precisely using provided information.\n"
                        "Do NOT hallucinate.\n"
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )

        return response.choices[0].message.content.strip()


    # =====================================
    # BUILD CONTEXT
    # =====================================

    def _build_context(self, chunks):

        return "\n\n".join(chunks[:15])


    # =====================================
    # BUILD PROMPT
    # =====================================

    def _build_prompt(self, question, context):

        return f"""
You are analyzing a software codebase.

Use the CODEBASE CONTEXT to answer the QUESTION.

Rules:
- Answer ONLY from context
- Do NOT hallucinate
- If overview question → explain architecture clearly
- If flow question → explain execution flow
- If setup question → explain installation/setup steps

CODEBASE CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""


    # =====================================
    # BUILD API SUMMARY (CRITICAL)
    # =====================================

    def _build_api_summary(self, repo_name: str):

        results = self.retriever.vector_store.collection.get()

        metas = results.get("metadatas", [])

        apis = []

        for meta in metas:

            if meta.get("repo_name") != repo_name:
                continue

            routes = meta.get("api_routes")

            if routes:
                apis.extend(routes)

        unique_apis = sorted(list(set(apis)))

        if not unique_apis:
            return None

        summary = f"Total APIs: {len(unique_apis)}\n\nAPI Endpoints:\n"

        for api in unique_apis:
            summary += f"- {api}\n"

        return summary