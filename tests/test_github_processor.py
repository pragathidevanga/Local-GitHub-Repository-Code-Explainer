"""Unit tests for GitHub processor and URL validation."""

from pathlib import Path
from backend.github_processor import RepositoryCloner
from backend.utils import parse_github_url


def test_parse_github_url_valid():
    valid, owner, repo, norm_url = parse_github_url("https://github.com/torvalds/linux")
    assert valid is True
    assert owner == "torvalds"
    assert repo == "linux"
    assert norm_url == "https://github.com/torvalds/linux.git"


def test_parse_github_url_with_git_suffix():
    valid, owner, repo, norm_url = parse_github_url("https://github.com/psf/black.git/")
    assert valid is True
    assert owner == "psf"
    assert repo == "black"
    assert norm_url == "https://github.com/psf/black.git"


def test_parse_github_url_invalid():
    valid, owner, repo, msg = parse_github_url("https://invalid-url.com/something")
    assert valid is False
    assert "Invalid GitHub URL format" in msg


def test_clone_nonexistent_repo():
    success, owner, temp_dir, repo_name, err = RepositoryCloner.clone_to_temp("https://github.com/nonexistent_user_9999/nonexistent_repo_9999")
    assert success is False
    assert temp_dir is None
    assert "Repository not found" in err or "Git clone failed" in err
