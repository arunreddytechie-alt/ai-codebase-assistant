from services.codebase_assistant.ingestion.github_loader import GitHubLoader
from services.codebase_assistant.ingestion.file_scanner import FileScanner
from services.codebase_assistant.ingestion.chunk_extractor import ChunkExtractor


print("\n=== TEST 1: CHUNK EXTRACTION ===\n")

# Step 1: clone repo
loader = GitHubLoader()

repo_url = "https://github.com/arunreddytechie-alt/resume-analyzer"

repo_path = loader.clone_repo(repo_url)

print("\nRepo cloned to:", repo_path)


# Step 2: scan files
scanner = FileScanner(repo_path, "resume-analyzer")

files = scanner.scan()

print("\nTotal files found:", len(files))


# Step 3: extract chunks
extractor = ChunkExtractor()

all_chunks = []

for file_info in files:

    chunks = extractor.extract_chunks(file_info)

    all_chunks.extend(chunks)


print("\nTotal chunks extracted:", len(all_chunks))


# Step 4: show sample chunk
print("\nSample chunk:\n")

sample = all_chunks[0]

print("Component ID:", sample["component_id"])

print("Metadata:", sample["metadata"])

print("Code preview:\n", sample["code"][:200])


print("\nTEST 1 PASSED\n")