# tests/verify_api_metadata.py

from services.codebase_assistant.vectorstore.chroma_store import ChromaStore

store = ChromaStore()

results = store.collection.get()

for meta in results["metadatas"]:

    if meta.get("api_routes"):

        print(meta["api_routes"])