import json
from typing import List, Dict

from services.codebase_assistant.vectorstore.chroma_store import ChromaStore


class HybridRetriever:

    def __init__(self, graph_path="data/graph/graph.json"):

        print("Initializing Hybrid Retriever...")

        self.vector_store = ChromaStore()
        self.graph = self._load_graph(graph_path)

        print(f"Graph loaded with {len(self.graph)} nodes")


    # =====================================
    # MAIN ENTRYPOINT
    # =====================================

    def retrieve(
        self,
        query: str,
        repo_name: str,
        intent: str = "general",
        top_k: int = 5,
        expand_k: int = 2
    ):

        print(f"\nRetrieving for query: {query}")
        print(f"Repo: {repo_name}")
        print(f"Intent: {intent}")

        if intent == "overview":
            return self._retrieve_overview(repo_name)

        elif intent == "setup":
            return self._retrieve_setup(repo_name)

        elif intent == "api":
            return self._retrieve_api(repo_name)

        elif intent == "architecture":
            return self._retrieve_architecture(repo_name)

        elif intent == "dependency":
            return self._retrieve_dependencies(repo_name)

        return self._retrieve_semantic_graph(query, repo_name, top_k, expand_k)


    # =====================================
    # API RETRIEVAL — FIXED VERSION
    # =====================================

    def _retrieve_api(self, repo_name):

        print("Scanning vector DB for API metadata...")

        results = self.vector_store.collection.get()

        docs = results.get("documents", [])
        metas = results.get("metadatas", [])

        api_chunks = []

        for i, meta in enumerate(metas):

            if meta.get("repo_name") != repo_name:
                continue

            api_routes = meta.get("api_routes")
            is_api = meta.get("is_api", False)

            # CRITICAL FIX: use api_routes metadata
            if api_routes and api_routes != "None":

                print(f"Found API file: {meta.get('file_name')}")
                print(f"Routes: {api_routes}")

                chunk = f"""
FILE: {meta.get('file_name')}

API ROUTES:
{api_routes}

CODE:
{docs[i]}
"""

                api_chunks.append(chunk)

        print(f"API chunks found: {len(api_chunks)}")

        return api_chunks[:20]


    # =====================================
    # OVERVIEW
    # =====================================

    def _retrieve_overview(self, repo_name):

        results = self.vector_store.collection.get()

        docs = results["documents"]
        metas = results["metadatas"]

        chunks = []

        for i, meta in enumerate(metas):

            if meta["repo_name"] != repo_name:
                continue

            file = meta.get("file_name", "").lower()

            if (
                "readme" in file
                or file in ["main.py", "app.py", "server.py"]
                or meta.get("chunk_type") in ["file", "class"]
            ):
                chunks.append(docs[i])

        print(f"Overview chunks: {len(chunks)}")

        return chunks[:15]


    # =====================================
    # SETUP
    # =====================================

    def _retrieve_setup(self, repo_name):

        results = self.vector_store.collection.get()

        docs = results["documents"]
        metas = results["metadatas"]

        chunks = []

        for i, meta in enumerate(metas):

            if meta["repo_name"] != repo_name:
                continue

            file = meta.get("file_name", "").lower()

            if (
                "readme" in file
                or "requirements" in file
                or "dockerfile" in file
            ):
                chunks.append(docs[i])

        print(f"Setup chunks: {len(chunks)}")

        return chunks[:15]


    # =====================================
    # ARCHITECTURE
    # =====================================

    def _retrieve_architecture(self, repo_name):

        results = self.vector_store.collection.get()

        docs = results["documents"]
        metas = results["metadatas"]

        chunks = []

        for i, meta in enumerate(metas):

            if meta["repo_name"] != repo_name:
                continue

            if meta.get("chunk_type") in ["file", "class"]:
                chunks.append(docs[i])

        print(f"Architecture chunks: {len(chunks)}")

        return chunks[:15]


    # =====================================
    # DEPENDENCIES
    # =====================================

    def _retrieve_dependencies(self, repo_name):

        results = self.vector_store.collection.get()

        docs = results["documents"]
        metas = results["metadatas"]

        chunks = []

        for i, meta in enumerate(metas):

            if meta["repo_name"] != repo_name:
                continue

            file = meta.get("file_name", "").lower()

            if "requirements" in file:
                chunks.append(docs[i])

        print(f"Dependency chunks: {len(chunks)}")

        return chunks[:10]


    # =====================================
    # SEMANTIC + GRAPH
    # =====================================

    def _retrieve_semantic_graph(self, query, repo_name, top_k, expand_k):

        print("Using semantic retrieval")

        semantic = self.vector_store.search(
            query=query,
            repo_name=repo_name,
            top_k=top_k
        )

        docs = semantic.get("documents", [[]])[0]
        metas = semantic.get("metadatas", [[]])[0]

        component_ids = []

        for meta in metas:
            comp = meta.get("component_id")
            if comp:
                component_ids.append(comp)

        expanded_ids = self._expand_graph(component_ids, expand_k)

        expanded_docs = self._fetch_chunks(expanded_ids, repo_name)

        merged = list(dict.fromkeys(docs + expanded_docs))

        print(f"Total chunks: {len(merged)}")

        return merged[:15]


    # =====================================
    # GRAPH EXPANSION
    # =====================================

    def _expand_graph(self, component_ids, depth):

        visited = set()
        stack = component_ids.copy()

        for _ in range(depth):

            next_nodes = []

            for node in stack:

                if node in visited:
                    continue

                visited.add(node)

                neighbors = self.graph.get(node, [])
                next_nodes.extend(neighbors)

            stack = next_nodes

        return list(visited)


    # =====================================
    # FETCH CHUNKS
    # =====================================

    def _fetch_chunks(self, component_ids, repo_name):

        results = self.vector_store.collection.get()

        docs = results["documents"]
        metas = results["metadatas"]

        chunks = []

        for i, meta in enumerate(metas):

            if meta["repo_name"] != repo_name:
                continue

            if meta.get("component_id") in component_ids:
                chunks.append(docs[i])

        return chunks


    def _load_graph(self, graph_path):

        try:
            with open(graph_path) as f:
                return json.load(f)
        except:
            return {}