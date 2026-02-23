import os
import shutil
from git import Repo
from urllib.parse import urlparse


class GitHubLoader:

    def __init__(self, base_dir="data/codebases"):

        self.base_dir = base_dir

        os.makedirs(self.base_dir, exist_ok=True)

    def clone_repo(self, github_url: str) -> str:

        repo_name = self._extract_repo_name(github_url)

        clone_path = os.path.join(self.base_dir, repo_name)

        # delete if exists
        if os.path.exists(clone_path):

            shutil.rmtree(clone_path)

        print(f"Cloning repo: {github_url}")

        Repo.clone_from(github_url, clone_path)

        print(f"Cloned to: {clone_path}")

        return clone_path

    def _extract_repo_name(self, github_url):

        path = urlparse(github_url).path

        repo_name = os.path.basename(path)

        if repo_name.endswith(".git"):

            repo_name = repo_name[:-4]

        return repo_name