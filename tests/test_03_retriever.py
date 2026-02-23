from services.codebase_assistant.vectorstore.chroma_store import ChromaStore


print("\n=== TEST 3: RETRIEVER TEST ===\n")


store = ChromaStore()

count = store.collection.count()

print("Chunks available:", count)


query = "upload resume"

print("\nQuery:", query)


results = store.search(query, top_k=5)


documents = results.get("documents", [[]])[0]


print("\nDocuments found:", len(documents))


for i, doc in enumerate(documents):

    print(f"\n--- Result {i+1} preview ---\n")

    print(doc[:200])


print("\nTEST 3 COMPLETED\n")