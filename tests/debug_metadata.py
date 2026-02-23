from services.codebase_assistant.vectorstore.chroma_store import ChromaStore

store = ChromaStore()

results = store.collection.get()

metas = results["metadatas"]

print("\nTotal chunks:", len(metas))

api_count = 0

for meta in metas:

    if meta.get("chunk_type") == "api":
        api_count += 1
        print(meta)

print("\nAPI chunks found:", api_count)