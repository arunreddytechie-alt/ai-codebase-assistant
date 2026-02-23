from services.codebase_assistant.ingestion.github_loader import GitHubLoader
from services.codebase_assistant.ingestion.file_scanner import FileScanner
from services.codebase_assistant.ingestion.chunk_extractor import ChunkExtractor
from services.codebase_assistant.vectorstore.chroma_store import ChromaStore


print("\n=== TEST 2: STORE CHUNKS INTO CHROMADB ===\n")


# Step 1: clone repo
loader = GitHubLoader()

repo_url = "https://github.com/arunreddytechie-alt/resume-analyzer"

repo_path = loader.clone_repo(repo_url)


# Step 2: scan files
scanner = FileScanner(repo_path, "resume-analyzer")

files = scanner.scan()


# Step 3: extract chunks
extractor = ChunkExtractor()

all_chunks = []

for file_info in files:

    chunks = extractor.extract_chunks(file_info)

    all_chunks.extend(chunks)


print("\nChunks ready to store:", len(all_chunks))


# Step 4: store in ChromaDB
store = ChromaStore()

store.store_chunks(all_chunks)


# Step 5: verify storage
count = store.collection.count()

print("\nChunks stored in DB:", count)


print("\nTEST 2 COMPLETED\n")