import os
from openai import OpenAI


class IntentRouter:

    def __init__(self):

        self.client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )


    def detect_intent(self, question: str):

        prompt = f"""
Classify the user question into ONE of these intent types:

overview  → asking about architecture, purpose, or summary
api       → asking about APIs, endpoints, routes
flow      → asking how something works or execution flow
setup     → asking about installation, deployment, running
specific  → asking about specific function or implementation

Return ONLY one word from:
overview, api, flow, setup, specific

Question:
{question}
"""

        response = self.client.chat.completions.create(

            model="gpt-4o-mini",

            messages=[
                {
                    "role": "system",
                    "content": "You are an intent classifier."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0
        )

        intent = response.choices[0].message.content.strip().lower()

        print(f"Detected intent: {intent}")

        return intent