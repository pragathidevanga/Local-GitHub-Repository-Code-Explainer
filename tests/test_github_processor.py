import pytest

from backend.github_processor import GitHubProcessor


def test_valid_github_url() -> None:
    owner, repo, url = GitHubProcessor.validate_url("https://github.com/example/repo")
    assert (owner, repo) == ("example", "repo")
    assert url.endswith("example/repo.git")


def test_git_url_variants_are_normalized() -> None:
    owner, repo, url = GitHubProcessor.validate_url("https://github.com/example/repo.git/")
    assert repo == "repo"
    assert url == "https://github.com/example/repo.git"


@pytest.mark.parametrize("url", [
    "http://github.com/example/repo",
    "https://gitlab.com/example/repo",
    "https://github.com/example",
    "not-a-url",
])
def test_invalid_url_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        GitHubProcessor.validate_url(url)
