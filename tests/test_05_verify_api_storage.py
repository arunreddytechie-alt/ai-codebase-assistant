from services.codebase_assistant.vectorstore.chroma_store import ChromaStore

print("\n=== TEST 5: VERIFY API METADATA IN VECTOR DB ===\n")

store = ChromaStore()

results = store.collection.get()

metas = results.get("metadatas", [])

api_found = False

for meta in metas:

    repo = meta.get("repo_name")
    file = meta.get("file_name")
    routes = meta.get("api_routes")

    if routes:
        api_found = True
        print(f"Repo: {repo}")
        print(f"File: {file}")
        print(f"Routes: {routes}")
        print("-" * 40)

if not api_found:
    print("ERROR: No API routes stored in vector DB")

else:
    print("\nTEST 5 PASSED: API metadata exists in DB")