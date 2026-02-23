import os
from openai import OpenAI
from dotenv import load_dotenv

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

        print("LLM Service ready")


    # =====================================
    # MAIN ENTRYPOINT
    # =====================================

    def ask(self, question: str, repo_name: str):

        print(f"\nProcessing question: {question}")

        # Step 1: Retrieve relevant chunks
        chunks = self.retriever.retrieve(
            query=question,
            repo_name=repo_name
        )

        print(f"Chunks retrieved: {len(chunks)}")

        if not chunks:
            return "No relevant information found in this repository."

        # Step 2: Build context
        context = self._build_context(chunks)

        print("\nContext preview:")
        print(context[:500])


        # Step 3: Build prompt
        prompt = self._build_prompt(question, context)


        # Step 4: Call OpenAI
        response = self.client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert software engineer. "
                        "Answer questions using ONLY the provided code context. "
                        "Do NOT hallucinate."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )


        answer = response.choices[0].message.content.strip()

        return answer


    # =====================================
    # BUILD CONTEXT
    # =====================================

    def _build_context(self, chunks):

        context = "\n\n".join(chunks[:10])  # limit context size

        return context


    # =====================================
    # BUILD PROMPT
    # =====================================

    def _build_prompt(self, question, context):

        prompt = f"""
You are analyzing a software codebase.

Answer the question using ONLY the provided code context.

If the answer is not present in the context, say:
"I cannot find this in the codebase."

CODEBASE CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""

        return prompt