import os
from typing import List, Dict


# ==========================================
# SUPPORTED EXTENSIONS WITH LANGUAGE TYPE
# ==========================================

SUPPORTED_EXTENSIONS = {

    # Source code
    ".java": "java",
    ".py": "python",
    ".js": "javascript",
    ".ts": "typescript",

    # Documentation
    ".md": "markdown",
    ".txt": "text",

    # Config
    ".yaml": "yaml",
    ".yml": "yaml",
    ".json": "json",
    ".xml": "xml",
    ".ini": "config",
    ".cfg": "config",

    # Shell / infra
    ".sh": "shell",
    ".env": "env",

    # Build / dependency files
    ".gradle": "gradle",
    ".properties": "properties"
}


# ==========================================
# SPECIAL FILENAMES WITHOUT EXTENSION
# ==========================================

SUPPORTED_FILENAMES = {

    "Dockerfile": "docker",
    "docker-compose.yml": "docker",
    "docker-compose.yaml": "docker",

    "Makefile": "makefile",

    "requirements.txt": "requirements",
    "README": "markdown",
    "README.md": "markdown",
    "README.txt": "text",

    ".env": "env"
}


# ==========================================
# EXCLUDED DIRECTORIES
# ==========================================

EXCLUDED_DIRS = {

    ".git",
    "node_modules",
    "target",
    "build",
    "__pycache__",
    ".idea",
    ".vscode",
    "venv",
    "dist",
    ".next",
    ".pytest_cache",
    ".mypy_cache"
}


# ==========================================
# FILE SCANNER CLASS
# ==========================================

class FileScanner:

    def __init__(self, root_path: str, repo_name: str):

        self.root_path = root_path
        self.repo_name = repo_name

    # ======================================
    # MAIN SCAN FUNCTION
    # ======================================

    def scan(self) -> List[Dict]:

        file_list = []

        for root, dirs, files in os.walk(self.root_path):

            # Remove excluded dirs in-place
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]

            for file in files:

                full_path = os.path.join(root, file)

                language = self._detect_language(file)

                if language:

                    file_info = {
                        "repo_name": self.repo_name,
                        "file_path": full_path,
                        "file_name": file,
                        "language": language
                    }

                    file_list.append(file_info)

        print(f"Found {len(file_list)} supported files")

        return file_list

    # ======================================
    # LANGUAGE DETECTION
    # ======================================

    def _detect_language(self, filename: str):

        # Check special filenames first
        if filename in SUPPORTED_FILENAMES:

            return SUPPORTED_FILENAMES[filename]

        # Check extension
        ext = os.path.splitext(filename)[1].lower()

        if ext in SUPPORTED_EXTENSIONS:

            return SUPPORTED_EXTENSIONS[ext]

        return None