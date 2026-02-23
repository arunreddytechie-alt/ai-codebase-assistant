import re
from typing import List, Dict


class ChunkExtractor:

    def __init__(self):
        pass


    # ==============================
    # PUBLIC ENTRYPOINT
    # ==============================

    def extract_chunks(self, file_info: Dict) -> List[Dict]:

        language = file_info["language"]

        if language == "java":
            return self._extract_java_chunks(file_info)

        elif language == "python":
            return self._extract_python_chunks(file_info)

        else:
            return self._extract_generic_chunks(file_info)


    # ==============================
    # READ FILE
    # ==============================

    def _read_file(self, file_path: str) -> str:

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()

        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            return ""


    # ==============================
    # GENERATE UNIQUE CHUNK ID
    # ==============================

    def _generate_chunk_id(self, file_info: Dict, component_id: str) -> str:

        repo = file_info["repo_name"]
        path = file_info["file_path"]

        return f"{repo}:{path}:{component_id}"


    # ==============================
    # FASTAPI ROUTE EXTRACTOR
    # ==============================

    def _extract_fastapi_routes(self, code: str):

        routes = []

        pattern = r'@(app|router)\.(get|post|put|delete|patch)\(["\']([^"\']+)["\']'

        matches = re.finditer(pattern, code)

        for match in matches:

            routes.append({
                "method": match.group(2).upper(),
                "path": match.group(3)
            })

        return routes


    # ==============================
    # PYTHON EXTRACTION (FIXED FOR CHROMADB)
    # ==============================

    def _extract_python_chunks(self, file_info: Dict) -> List[Dict]:

        file_path = file_info["file_path"]
        code = self._read_file(file_path)

        if not code:
            return []

        chunks = []

        class_name = self._extract_python_class_name(code)
        functions = self._extract_python_functions(code)

        # Detect all API routes at file level
        api_routes = self._extract_fastapi_routes(code)

        is_api_file = len(api_routes) > 0


        # ==============================
        # FUNCTION CHUNKS
        # ==============================

        for func in functions:

            if class_name:
                component_id = f"{class_name}.{func['function_name']}"
            else:
                component_id = func["function_name"]

            chunk_id = self._generate_chunk_id(file_info, component_id)

            func_routes = self._extract_fastapi_routes(func["function_code"])

            metadata = {
                "repo_name": file_info["repo_name"],
                "file_path": file_path,
                "file_name": file_info["file_name"],
                "language": "python",

                "component_id": component_id,
                "function_name": func["function_name"],
                "class_name": class_name,

                "chunk_type": "api" if func_routes else "function",
                "is_api": bool(func_routes),

                "framework": "fastapi" if func_routes else None
            }

            # CRITICAL FIX: store api_routes as STRING (not list/dict)
            if func_routes:

                routes_str = []

                for route in func_routes:
                    routes_str.append(f"{route['method']} {route['path']}")

                metadata["api_routes"] = ", ".join(routes_str)

            chunks.append({
                "component_id": component_id,
                "chunk_id": chunk_id,
                "code": func["function_code"],
                "metadata": metadata
            })


        # ==============================
        # FILE LEVEL CHUNK
        # ==============================

        component_id = file_info["file_name"]
        chunk_id = self._generate_chunk_id(file_info, component_id)

        file_metadata = {
            "repo_name": file_info["repo_name"],
            "file_path": file_path,
            "file_name": file_info["file_name"],
            "language": "python",

            "component_id": component_id,

            "chunk_type": "file",
            "is_api": is_api_file,

            "framework": "fastapi" if is_api_file else None
        }

        # CRITICAL FIX: store api_routes as STRING
        if api_routes:

            routes_str = []

            for route in api_routes:
                routes_str.append(f"{route['method']} {route['path']}")

            file_metadata["api_routes"] = ", ".join(routes_str)

        chunks.append({
            "component_id": component_id,
            "chunk_id": chunk_id,
            "code": code,
            "metadata": file_metadata
        })

        return chunks


    # ==============================
    # PYTHON HELPERS
    # ==============================

    def _extract_python_class_name(self, code: str):

        match = re.search(r"class\s+(\w+)\s*:", code)

        return match.group(1) if match else None


    def _extract_python_functions(self, code: str):

        functions = []

        pattern = r"def\s+(\w+)\s*\("

        for match in re.finditer(pattern, code):

            func_name = match.group(1)
            start = match.start()

            func_code = self._extract_python_block(code, start)

            functions.append({
                "function_name": func_name,
                "function_code": func_code
            })

        return functions


    def _extract_python_block(self, code: str, start_index: int):

        lines = code[start_index:].split("\n")

        block = []
        indent = None

        for line in lines:

            if indent is None:
                indent = len(line) - len(line.lstrip())
                block.append(line)
                continue

            current_indent = len(line) - len(line.lstrip())

            if line.strip() == "" or current_indent > indent:
                block.append(line)
            else:
                break

        return "\n".join(block)


    # ==============================
    # GENERIC FILE
    # ==============================

    def _extract_generic_chunks(self, file_info: Dict):

        code = self._read_file(file_info["file_path"])

        if not code:
            return []

        component_id = file_info["file_name"]
        chunk_id = self._generate_chunk_id(file_info, component_id)

        return [{
            "component_id": component_id,
            "chunk_id": chunk_id,
            "code": code,
            "metadata": {
                "repo_name": file_info["repo_name"],
                "file_path": file_info["file_path"],
                "file_name": file_info["file_name"],
                "language": file_info["language"],
                "component_id": component_id,
                "chunk_type": "file"
            }
        }]


    # ==============================
    # JAVA EXTRACTION
    # ==============================

    def _extract_java_chunks(self, file_info: Dict):

        code = self._read_file(file_info["file_path"])

        if not code:
            return []

        class_name = self._extract_java_class_name(code)

        component_id = class_name
        chunk_id = self._generate_chunk_id(file_info, component_id)

        return [{
            "component_id": component_id,
            "chunk_id": chunk_id,
            "code": code,
            "metadata": {
                "repo_name": file_info["repo_name"],
                "file_path": file_info["file_path"],
                "file_name": file_info["file_name"],
                "language": "java",
                "component_id": component_id,
                "chunk_type": "class"
            }
        }]


    def _extract_java_class_name(self, code: str):

        match = re.search(r"class\s+(\w+)", code)

        return match.group(1) if match else "UnknownClass"