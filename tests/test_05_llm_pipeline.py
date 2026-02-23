from services.codebase_assistant.llm.llm_service import LLMService


print("\n=== TEST 5: FULL LLM PIPELINE ===\n")


llm = LLMService()


question = "What does this codebase do?"


answer = llm.ask(question)


print("\nQuestion:", question)

print("\nAnswer:\n")

print(answer)


print("\nTEST 5 DONE\n")