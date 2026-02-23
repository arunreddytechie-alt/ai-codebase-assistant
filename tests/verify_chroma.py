from services.codebase_assistant.vectorstore.chroma_store import ChromaStore

print("\n=== VERIFYING CHROMADB ===\n")

store = ChromaStore()

count = store.collection.count()

print(f"Total chunks stored: {count}")

if count == 0:
    print("\nERROR: No data in vector DB")
    exit(1)

data = store.collection.get(limit=5)

print("\nSample IDs:")
for id in data["ids"]:
    print(id)

print("\nSample metadata:")
for meta in data["metadatas"]:
    print(meta)

print("\nChromaDB verification SUCCESS")