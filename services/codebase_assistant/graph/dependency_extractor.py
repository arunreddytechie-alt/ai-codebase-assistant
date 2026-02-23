import re
import json
import os
from typing import List, Dict


class DependencyExtractor:

    def __init__(self, output_path="data/graph/graph.json"):

        self.output_path = output_path

        self.graph = {}

        self.class_method_map = {}

    # =====================================
    # BUILD GRAPH ENTRYPOINT
    # =====================================

    def build_graph(self, chunks: List[Dict]):

        print("\nBuilding dependency graph...")

        # Step 1: Build lookup map
        self._build_component_lookup(chunks)

        # Step 2: Extract dependencies
        for chunk in chunks:

            component_id = chunk["component_id"]

            code = chunk["code"]

            dependencies = self._extract_dependencies(code)

            resolved = self._resolve_dependencies(dependencies)

            self.graph[component_id] = resolved

        # Step 3: Save graph
        self._save_graph()

        print(f"Graph built with {len(self.graph)} nodes")

        return self.graph

    # =====================================
    # BUILD LOOKUP MAP
    # =====================================

    def _build_component_lookup(self, chunks):

        for chunk in chunks:

            component_id = chunk["component_id"]

            metadata = chunk["metadata"]

            class_name = metadata.get("class_name")

            method_name = metadata.get("method_name")

            if class_name and method_name:

                key = f"{class_name}.{method_name}"

                self.class_method_map[key] = component_id

    # =====================================
    # EXTRACT RAW DEPENDENCIES
    # =====================================

    def _extract_dependencies(self, code: str):

        pattern = r"(\w+)\.(\w+)\("

        matches = re.findall(pattern, code)

        dependencies = []

        for match in matches:

            class_name = match[0]
            method_name = match[1]

            dependencies.append(f"{class_name}.{method_name}")

        return dependencies

    # =====================================
    # RESOLVE TO VALID COMPONENTS
    # =====================================

    def _resolve_dependencies(self, dependencies):

        resolved = []

        for dep in dependencies:

            if dep in self.class_method_map:

                resolved.append(dep)

        return resolved

    # =====================================
    # SAVE GRAPH
    # =====================================

    def _save_graph(self):

        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)

        with open(self.output_path, "w") as f:

            json.dump(self.graph, f, indent=2)

        print(f"Graph saved to {self.output_path}")