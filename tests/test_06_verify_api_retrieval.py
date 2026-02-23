from services.codebase_assistant.retrieval.hybrid_retriever import HybridRetriever

print("\n=== TEST 6: VERIFY API RETRIEVAL ===\n")

retriever = HybridRetriever()

chunks = retriever.retrieve(
    query="how many api",
    repo_name="aws-rag-assistant",
    intent="api"
)

print(f"\nChunks returned: {len(chunks)}\n")

for i, chunk in enumerate(chunks):

    print(f"--- Chunk {i+1} ---")
    print(chunk[:200])
    print()