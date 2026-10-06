from __future__ import annotations

import io
import os
import shutil
from pathlib import Path
from urllib.parse import urlparse
from zipfile import ZipFile, BadZipFile

import requests

try:
    from git import Repo
except ImportError:  # pragma: no cover
    Repo = None

from .utils import safe_job_id


class GitHubProcessor:
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def validate_url(url: str) -> tuple[str, str, str]:
        parsed = urlparse(url.strip())
        if parsed.scheme != "https" or parsed.netloc.lower() not in {"github.com", "www.github.com"}:
            raise ValueError("Please provide a public HTTPS GitHub repository URL.")
        parts = [p for p in parsed.path.strip("/").split("/") if p]
        if len(parts) < 2:
            raise ValueError("GitHub URL must look like https://github.com/owner/repository")
        owner, repo = parts[0], parts[1].removesuffix(".git")
        if not owner or not repo:
            raise ValueError("Invalid GitHub repository URL.")
        clean_url = f"https://github.com/{owner}/{repo}.git"
        return owner, repo, clean_url

    def clone(self, url: str) -> tuple[Path, str, str, str]:
        owner, repo_name, clone_url = self.validate_url(url)
        destination = self.root / safe_job_id()
        os.environ.setdefault("GIT_TERMINAL_PROMPT", "0")

        if Repo is not None:
            try:
                repo = Repo.clone_from(
                    clone_url,
                    destination,
                    depth=1,
                    single_branch=True,
                    no_checkout=False,
                )
                branch = repo.active_branch.name if not repo.head.is_detached else None
                return destination, owner, repo_name, branch or "unknown"
            except Exception:
                shutil.rmtree(destination, ignore_errors=True)

        # Deployment-safe fallback when the runtime does not provide a Git executable.
        # This still retrieves the complete public repository snapshot without executing it.
        branch = self._default_branch(owner, repo_name)
        archive_url = f"https://github.com/{owner}/{repo_name}/archive/refs/heads/{branch}.zip"
        try:
            response = requests.get(
                archive_url,
                timeout=(10, 60),
                headers={"User-Agent": "Local-GitHub-Repository-Code-Explainer/2.0"},
            )
            response.raise_for_status()
            destination.mkdir(parents=True, exist_ok=True)
            self._extract_zip_safely(response.content, destination)
            return destination, owner, repo_name, branch
        except (requests.RequestException, BadZipFile, OSError, ValueError) as exc:
            shutil.rmtree(destination, ignore_errors=True)
            raise RuntimeError(f"Unable to retrieve the public GitHub repository: {exc}") from exc

    @staticmethod
    def _default_branch(owner: str, repo_name: str) -> str:
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        response = requests.get(
            api_url,
            timeout=(10, 20),
            headers={
                "Accept": "application/vnd.github+json",
                "User-Agent": "Local-GitHub-Repository-Code-Explainer/2.0",
            },
        )
        response.raise_for_status()
        data = response.json()
        branch = data.get("default_branch")
        if not branch:
            raise ValueError("GitHub did not return a default branch for this repository.")
        return str(branch)

    @staticmethod
    def _extract_zip_safely(data: bytes, destination: Path) -> None:
        with ZipFile(io.BytesIO(data)) as archive:
            members = archive.infolist()
            if not members:
                raise ValueError("GitHub returned an empty repository archive.")
            root_prefix = members[0].filename.split("/", 1)[0] + "/"
            for member in members:
                name = member.filename
                relative = name[len(root_prefix) :] if name.startswith(root_prefix) else name
                if not relative or relative.endswith("/"):
                    continue
                target = destination / relative
                target_parent = target.parent.resolve()
                if not str(target_parent).startswith(str(destination.resolve())):
                    raise ValueError("Repository archive contained an unsafe path.")
                target_parent.mkdir(parents=True, exist_ok=True)
                with archive.open(member) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)

    @staticmethod
    def cleanup(path: Path) -> None:
        shutil.rmtree(path, ignore_errors=True)
