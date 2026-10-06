"""GitHub repository cloner using shallow GitPython operations."""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path
from typing import Generator, Tuple

import git

from backend.utils import parse_github_url


class RepositoryCloner:
    """Manages cloning and temporary directory lifetime for GitHub repositories."""

    @staticmethod
    def clone_to_temp(url: str) -> Tuple[bool, str, Path | None, str, str]:
        """Shallow clone a public GitHub repository into a temporary directory.

        Args:
            url: Public HTTPS GitHub repository URL.

        Returns:
            Tuple of (success, owner, temp_path, repo_name, error_message)
        """
        valid, owner, repo_name, normalized_url = parse_github_url(url)
        if not valid:
            return False, "", None, "", normalized_url  # normalized_url contains error_message here

        temp_dir = Path(tempfile.mkdtemp(prefix="repo_explainer_"))

        try:
            # Environment variables to prevent git interactive authentication prompts
            clone_env = os.environ.copy()
            clone_env["GIT_TERMINAL_PROMPT"] = "0"
            clone_env["GIT_ASKPASS"] = "echo"

            git.Repo.clone_from(
                normalized_url,
                temp_dir,
                depth=1,
                env=clone_env,
                multi_options=["--single-branch"],
            )
            return True, owner, temp_dir, repo_name, ""
        except git.exc.GitCommandError as exc:
            RepositoryCloner.cleanup(temp_dir)
            err_msg = str(exc)
            if "Repository not found" in err_msg or "Could not resolve host" in err_msg or "404" in err_msg:
                return False, owner, None, repo_name, "Repository not found or network host unreachable. Please verify the URL."
            if "Authentication failed" in err_msg or "terminal prompts disabled" in err_msg or "403" in err_msg:
                return False, owner, None, repo_name, "Repository appears to be private or requires authentication. Only public repositories are supported."
            return False, owner, None, repo_name, f"Git clone failed: {err_msg[:200]}"
        except Exception as exc:
            RepositoryCloner.cleanup(temp_dir)
            return False, owner, None, repo_name, f"Unexpected clone error: {str(exc)[:200]}"

    @staticmethod
    def cleanup(target_dir: Path | str | None) -> None:
        """Safely remove temporary cloned repository directory."""
        if not target_dir:
            return
        path = Path(target_dir)
        if path.exists() and path.is_dir():
            # Handle Windows read-only file permissions inside .git
            def remove_readonly(func, subpath, _):
                try:
                    os.chmod(subpath, 0o777)
                    func(subpath)
                except Exception:
                    pass

            try:
                shutil.rmtree(path, onerror=remove_readonly)
            except Exception:
                pass
