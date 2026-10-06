"""End-to-end test analyzing a real public GitHub repository."""

from backend.main import process_repository_service


def test_end_to_end_public_repo_analysis():
    # Test on a small public repository owned by octocat
    test_url = "https://github.com/octocat/Hello-World"
    response = process_repository_service(test_url)

    assert response.success is True
    assert response.url == test_url
    assert response.inventory is not None
    assert response.inventory.owner == "octocat"
    assert response.inventory.repo_name == "Hello-World"
    assert response.inventory.total_files > 0

    assert response.smart_context is not None
    assert response.smart_context.file_count > 0

    assert response.prompt is not None
    assert "octocat" in response.prompt
    assert "Hello-World" in response.prompt

    assert response.timing.total_ms > 0
    assert response.timing.clone_ms > 0
    assert response.timing.scan_ms > 0
