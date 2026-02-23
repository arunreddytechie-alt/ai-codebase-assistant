import argparse
import os

from services.codebase_assistant.ingestion.github_loader import GitHubLoader
from services.codebase_assistant.ingestion.file_scanner import FileScanner
from services.codebase_assistant.ingestion.chunk_extractor import ChunkExtractor
from services.codebase_assistant.vectorstore.chroma_store import ChromaStore
from services.codebase_assistant.graph.dependency_extractor import DependencyExtractor

# ==========================================
# LOCAL INGESTION PIPELINE
# ==========================================

def ingest_local(repo_path: str, repo_name: str):

    print(f"\nStarting ingestion for repo: {repo_name}")
    print(f"Repo path: {repo_path}")

    # Step 1: Scan files
    scanner = FileScanner(repo_path, repo_name)

    files = scanner.scan()

    print(f"Total supported files found: {len(files)}")

    # Step 2: Extract chunks
    extractor = ChunkExtractor()

    all_chunks = []

    for file_info in files:

        chunks = extractor.extract_chunks(file_info)

        all_chunks.extend(chunks)

    print(f"\nTotal chunks extracted: {len(all_chunks)}")
    # Step 3: Store in Vector DB
    print("\nStoring chunks in vector DB...")
    vector_store = ChromaStore()
    try:
        vector_store.store_chunks(all_chunks)
    except Exception as e:
        print("\nCHROMADB ERROR:", str(e))
        raise e
    
    # Step 4: Build dependency graph
    extractor = DependencyExtractor()
    extractor.build_graph(all_chunks)

    # Debug print first few chunks
    print("\nSample chunks:")

    for chunk in all_chunks[:5]:
        print(f"  {chunk['component_id']}")

    return all_chunks


# ==========================================
# GITHUB INGESTION PIPELINE
# ==========================================

def ingest_github(github_url: str):

    loader = GitHubLoader()

    local_path = loader.clone_repo(github_url)

    repo_name = os.path.basename(local_path)

    print(f"\nRe-ingesting repo: {repo_name}")

    # NEW: delete existing repo data
    store = ChromaStore()

    results = store.collection.get()

    ids_to_delete = []
    metadatas = results.get("metadatas", [])
    ids = results.get("ids", [])

    for i, meta in enumerate(metadatas):

        if meta.get("repo_name") == repo_name:

            ids_to_delete.append(ids[i])

    if ids_to_delete:

        print(f"Deleting {len(ids_to_delete)} old chunks")

        store.collection.delete(ids=ids_to_delete)

    # continue ingestion
    return ingest_local(local_path, repo_name)


# ==========================================
# MAIN ENTRYPOINT
# ==========================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--path",
        help="Local repository path"
    )

    parser.add_argument(
        "--repo",
        help="Repository name"
    )

    parser.add_argument(
        "--github",
        help="GitHub repository URL"
    )

    args = parser.parse_args()

    if args.github:

        chunks = ingest_github(args.github)

        print(f"\nGitHub ingestion complete. Total chunks: {len(chunks)}")

    elif args.path and args.repo:

        chunks = ingest_local(args.path, args.repo)

        print(f"\nLocal ingestion complete. Total chunks: {len(chunks)}")

    else:

        print("\nError: Provide either:")
        print("  --github <repo_url>")
        print("OR")
        print("  --path <repo_path> --repo <repo_name>")


if __name__ == "__main__":
    main()