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
    # LOAD GRAPH
    # =====================================

    def _load_graph(self, graph_path):

        try:
            with open(graph_path, "r") as f:
                return json.load(f)

        except Exception as e:

            print(f"Graph load failed: {e}")

            return {}


    # =====================================
    # MAIN RETRIEVAL FUNCTION
    # =====================================

    def retrieve(self, query: str, repo_name: str, top_k=5, expand_k=3):

        print(f"\nRetrieving for query: {query}")
        print(f"Repo filter: {repo_name}")

        # =====================================
        # STEP 1: SEMANTIC SEARCH (repo filtered)
        # =====================================

        semantic_results = self.vector_store.search(query, repo_name, top_k)

        semantic_ids = semantic_results.get("ids", [[]])[0]
        semantic_docs = semantic_results.get("documents", [[]])[0]
        semantic_metadata = semantic_results.get("metadatas", [[]])[0]

        print(f"Semantic matches found: {len(semantic_ids)}")

        # =====================================
        # STEP 2: GET COMPONENT IDS
        # =====================================

        component_ids = []

        for meta in semantic_metadata:

            comp_id = meta.get("component_id")

            if comp_id:
                component_ids.append(comp_id)

        # =====================================
        # STEP 3: GRAPH EXPANSION
        # =====================================

        expanded_component_ids = self._expand_graph(component_ids, expand_k)

        print(f"Expanded components: {len(expanded_component_ids)}")

        expanded_chunks = self._fetch_chunks(
            component_ids=expanded_component_ids,
            repo_name=repo_name
        )

        # =====================================
        # STEP 4: PRIORITY CHUNKS (README / main / architecture)
        # =====================================

        priority_chunks = self._get_priority_chunks(repo_name)

        print(f"Priority chunks found: {len(priority_chunks)}")

        # =====================================
        # STEP 5: MERGE AND DEDUPLICATE
        # =====================================

        final_chunks = []

        seen = set()

        # Priority first
        for chunk in priority_chunks:
            if chunk not in seen:
                final_chunks.append(chunk)
                seen.add(chunk)

        # Then semantic
        for chunk in semantic_docs:
            if chunk not in seen:
                final_chunks.append(chunk)
                seen.add(chunk)

        # Then graph expanded
        for chunk in expanded_chunks:
            if chunk not in seen:
                final_chunks.append(chunk)
                seen.add(chunk)

        print(f"Total chunks returned: {len(final_chunks)}")

        return final_chunks[:15]


    # =====================================
    # GET PRIORITY CHUNKS
    # =====================================

    def _get_priority_chunks(self, repo_name: str):

        results = self.vector_store.collection.get()

        docs = results.get("documents", [])
        metas = results.get("metadatas", [])

        priority_chunks = []

        for i, meta in enumerate(metas):

            if meta.get("repo_name") != repo_name:
                continue

            file_name = meta.get("file_name", "").lower()

            chunk_type = meta.get("chunk_type", "")

            if (
                "readme" in file_name
                or "main.py" in file_name
                or "app.py" in file_name
                or chunk_type in ["file", "class"]
            ):
                priority_chunks.append(docs[i])

        return priority_chunks


    # =====================================
    # GRAPH EXPANSION
    # =====================================

    def _expand_graph(self, component_ids: List[str], depth=2):

        visited = set()
        stack = list(component_ids)
        result = set()

        current_depth = 0

        while stack and current_depth < depth:

            next_stack = []

            for comp in stack:

                if comp in visited:
                    continue

                visited.add(comp)

                result.add(comp)

                neighbors = self.graph.get(comp, [])

                next_stack.extend(neighbors)

            stack = next_stack

            current_depth += 1

        return list(result)


    # =====================================
    # FETCH CHUNKS FROM VECTOR DB (repo filtered)
    # =====================================

    def _fetch_chunks(self, component_ids: List[str], repo_name: str):

        results = self.vector_store.collection.get()

        docs = results.get("documents", [])
        metas = results.get("metadatas", [])

        chunks = []

        for i, meta in enumerate(metas):

            if meta.get("repo_name") != repo_name:
                continue

            comp_id = meta.get("component_id")

            if comp_id in component_ids:
                chunks.append(docs[i])

        return chunks