import chromadb
from sentence_transformers import SentenceTransformer


class ChromaStore:

    def __init__(self, persist_dir="db/chroma"):

        print("Initializing ChromaDB...")

        # FIX: use PersistentClient (not Client)
        self.client = chromadb.PersistentClient(
            path=persist_dir
        )

        self.collection = self.client.get_or_create_collection(
            name="codebase_chunks"
        )

        print("Loading embedding model...")

        self.embedding_model = SentenceTransformer(
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        print("Embedding model loaded")

    # =====================================
    # STORE CHUNKS
    # =====================================

    def store_chunks(self, chunks):

        if not chunks:
            print("No chunks to store")
            return

        documents = []
        metadatas = []
        ids = []

        for chunk in chunks:

            repo = chunk["metadata"]["repo_name"]
            file_path = chunk["metadata"]["file_path"]
            component = chunk["component_id"]

            chunk_id = f"{repo}:{file_path}:{component}"

            documents.append(chunk["code"])

            metadata = chunk["metadata"].copy()
            metadata["component_id"] = chunk_id

            metadatas.append(metadata)
            ids.append(chunk_id)

        print(f"Generating embeddings for {len(documents)} chunks...")

        embeddings = self.embedding_model.encode(documents).tolist()

        print("Storing in ChromaDB...")

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )

        print(f"Successfully stored {len(ids)} chunks")

    # =====================================
    # SEARCH
    # =====================================

    def search(self, query, repo_name=None, top_k=5):

        query_embedding = self.embedding_model.encode([query]).tolist()

        if repo_name:

            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k,
                where={"repo_name": repo_name}
            )
        else:

            results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=top_k
        )

        return results