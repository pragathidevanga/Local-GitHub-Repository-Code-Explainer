from pathlib import Path

from backend.job_manager import JobManager


def test_create_job_returns_immediately(tmp_path: Path) -> None:
    manager = JobManager(tmp_path)
    original = manager._run
    called = []

    def fake_run(job_id: str) -> None:
        called.append(job_id)

    manager._run = fake_run
    job = manager.create("https://github.com/example/repo")
    assert job.status == "queued"
    assert job.github_url.endswith("repo")
    job_obj = manager.get(job.job_id)
    assert job_obj is not None
    manager.executor.shutdown(wait=True)
    manager._run = original
    assert called == [job.job_id]
