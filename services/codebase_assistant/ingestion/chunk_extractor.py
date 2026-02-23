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
    # JAVA EXTRACTION
    # ==============================

    def _extract_java_chunks(self, file_info: Dict) -> List[Dict]:

        file_path = file_info["file_path"]
        code = self._read_file(file_path)

        if not code:
            return []

        chunks = []

        class_name = self._extract_java_class_name(code)

        methods = self._extract_java_methods(code)

        # METHOD CHUNKS
        for method in methods:

            component_id = f"{class_name}.{method['method_name']}"

            chunk_id = self._generate_chunk_id(file_info, component_id)

            chunk = {
                "component_id": component_id,
                "chunk_id": chunk_id,
                "code": method["method_code"],
                "metadata": {
                    "repo_name": file_info["repo_name"],
                    "file_path": file_path,
                    "file_name": file_info["file_name"],
                    "language": "java",
                    "class_name": class_name,
                    "method_name": method["method_name"],
                    "function_name": None,
                    "component_id": component_id,
                    "chunk_type": "method"
                }
            }

            chunks.append(chunk)

        # CLASS CHUNK
        component_id = class_name

        chunk_id = self._generate_chunk_id(file_info, component_id)

        class_chunk = {
            "component_id": component_id,
            "chunk_id": chunk_id,
            "code": code,
            "metadata": {
                "repo_name": file_info["repo_name"],
                "file_path": file_path,
                "file_name": file_info["file_name"],
                "language": "java",
                "class_name": class_name,
                "method_name": None,
                "function_name": None,
                "component_id": component_id,
                "chunk_type": "class"
            }
        }

        chunks.append(class_chunk)

        return chunks

    def _extract_java_class_name(self, code: str) -> str:

        pattern = r"class\s+(\w+)"

        match = re.search(pattern, code)

        if match:
            return match.group(1)

        return "UnknownClass"

    def _extract_java_methods(self, code: str) -> List[Dict]:

        methods = []

        pattern = r"(public|private|protected)\s+\w+\s+(\w+)\s*\([^)]*\)\s*\{"

        matches = re.finditer(pattern, code)

        for match in matches:

            method_name = match.group(2)

            start_index = match.start()

            method_code = self._extract_block(code, start_index)

            methods.append({
                "method_name": method_name,
                "method_code": method_code
            })

        return methods

    # ==============================
    # PYTHON EXTRACTION
    # ==============================

    def _extract_python_chunks(self, file_info: Dict) -> List[Dict]:

        file_path = file_info["file_path"]
        code = self._read_file(file_path)

        if not code:
            return []

        chunks = []

        class_name = self._extract_python_class_name(code)

        functions = self._extract_python_functions(code)

        for func in functions:

            if class_name:
                component_id = f"{class_name}.{func['function_name']}"
            else:
                component_id = func["function_name"]

            chunk_id = self._generate_chunk_id(file_info, component_id)

            chunk = {
                "component_id": component_id,
                "chunk_id": chunk_id,
                "code": func["function_code"],
                "metadata": {
                    "repo_name": file_info["repo_name"],
                    "file_path": file_path,
                    "file_name": file_info["file_name"],
                    "language": "python",
                    "class_name": class_name,
                    "method_name": None,
                    "function_name": func["function_name"],
                    "component_id": component_id,
                    "chunk_type": "function"
                }
            }

            chunks.append(chunk)

        return chunks

    def _extract_python_class_name(self, code: str):

        pattern = r"class\s+(\w+)\s*:"

        match = re.search(pattern, code)

        if match:
            return match.group(1)

        return None

    def _extract_python_functions(self, code: str) -> List[Dict]:

        functions = []

        pattern = r"def\s+(\w+)\s*\("

        matches = re.finditer(pattern, code)

        for match in matches:

            func_name = match.group(1)

            start_index = match.start()

            func_code = self._extract_python_block(code, start_index)

            functions.append({
                "function_name": func_name,
                "function_code": func_code
            })

        return functions

    def _extract_python_block(self, code: str, start_index: int) -> str:

        lines = code[start_index:].split("\n")

        block = []

        indent_level = None

        for line in lines:

            if indent_level is None:

                indent_level = len(line) - len(line.lstrip())

                block.append(line)

            else:

                current_indent = len(line) - len(line.lstrip())

                if line.strip() == "" or current_indent > indent_level:
                    block.append(line)
                else:
                    break

        return "\n".join(block)

    # ==============================
    # GENERIC FALLBACK
    # ==============================

    def _extract_generic_chunks(self, file_info: Dict) -> List[Dict]:

        file_path = file_info["file_path"]

        code = self._read_file(file_path)

        if not code:
            return []

        component_id = file_info["file_name"]

        chunk_id = self._generate_chunk_id(file_info, component_id)

        chunk = {
            "component_id": component_id,
            "chunk_id": chunk_id,
            "code": code,
            "metadata": {
                "repo_name": file_info["repo_name"],
                "file_path": file_path,
                "file_name": file_info["file_name"],
                "language": file_info["language"],
                "class_name": None,
                "method_name": None,
                "function_name": None,
                "component_id": component_id,
                "chunk_type": "file"
            }
        }

        return [chunk]

    # ==============================
    # JAVA BLOCK EXTRACTOR
    # ==============================

    def _extract_block(self, code: str, start_index: int) -> str:

        brace_count = 0
        index = start_index

        while index < len(code):

            if code[index] == "{":
                brace_count += 1

            elif code[index] == "}":
                brace_count -= 1

                if brace_count == 0:
                    return code[start_index:index + 1]

            index += 1

        return code[start_index:]