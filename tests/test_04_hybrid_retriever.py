from services.codebase_assistant.retrieval.hybrid_retriever import HybridRetriever


print("\n=== TEST 4: HYBRID RETRIEVER ===\n")

retriever = HybridRetriever()

query = "upload resume"

results = retriever.retrieve(query)

print("\nTotal chunks returned:", len(results))

for i, chunk in enumerate(results):
    print(f"\n--- Chunk {i+1} preview ---")
    print(chunk[:200])

print("\nTEST 4 DONE\n")