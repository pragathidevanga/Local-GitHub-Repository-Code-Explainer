from __future__ import annotations

import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .github_processor import GitHubProcessor
from .llm_service import LocalLLMService, build_prompt
from .models import JobStatusResponse, RepositoryReport
from .repository_analyzer import analyze_repository, select_context_files
from .utils import safe_job_id


@dataclass
class Job:
    job_id: str
    github_url: str
    status: str = "queued"
    stage: str = "queued"
    progress: int = 0
    message: str = "Waiting to start..."
    started_at: float = field(default_factory=time.perf_counter)
    timings: dict[str, float] = field(default_factory=dict)
    report: RepositoryReport | None = None
    explanation: str | None = None
    error: str | None = None


class JobManager:
    def __init__(self, repo_root: Path) -> None:
        self.processor = GitHubProcessor(repo_root)
        self.llm = LocalLLMService()
        self.jobs: dict[str, Job] = {}
        self.lock = threading.Lock()
        self.executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="repo-explainer")

    def create(self, github_url: str) -> Job:
        job = Job(job_id=safe_job_id(), github_url=github_url)
        with self.lock:
            self.jobs[job.job_id] = job
        self.executor.submit(self._run, job.job_id)
        return job

    def get(self, job_id: str) -> Job | None:
        with self.lock:
            return self.jobs.get(job_id)

    def _set(self, job: Job, **updates: Any) -> None:
        with self.lock:
            for key, value in updates.items():
                setattr(job, key, value)

    def _run(self, job_id: str) -> None:
        job = self.get(job_id)
        if not job:
            return
        clone_path: Path | None = None
        total_started = time.perf_counter()
        try:
            self._set(job, status="running", stage="validate", progress=5, message="Validating GitHub repository URL...")
            t = time.perf_counter()
            owner, repo_name, clone_url = self.processor.validate_url(job.github_url)
            job.timings["validation"] = time.perf_counter() - t

            self._set(job, stage="clone", progress=18, message="Cloning repository (shallow clone)...")
            t = time.perf_counter()
            clone_path, owner, repo_name, branch = self.processor.clone(clone_url)
            job.timings["clone"] = time.perf_counter() - t

            self._set(job, stage="scan", progress=40, message="Scanning repository files and folders...")
            t = time.perf_counter()
            raw_report = analyze_repository(clone_path)
            job.timings["scan"] = time.perf_counter() - t

            if raw_report["inspectable_files"] == 0:
                raise RuntimeError("The repository contains no inspectable files after excluding Git metadata and sensitive files.")

            self._set(job, stage="context", progress=58, message="Selecting the most relevant evidence for the local LLM...")
            t = time.perf_counter()
            selected, context_chars = select_context_files(
                raw_report["files"],
                max_files=int(__import__("os").getenv("MAX_LLM_FILES", "40")),
                max_file_size=int(__import__("os").getenv("MAX_LLM_FILE_SIZE", "18000")),
                max_total_chars=int(__import__("os").getenv("MAX_LLM_CONTEXT_CHARS", "24000")),
            )
            job.timings["context"] = time.perf_counter() - t

            self._set(job, stage="technology", progress=68, message="Detecting technologies from repository evidence...")
            t = time.perf_counter()
            # Technology detection was already computed during the single scan. This stage is intentionally a fast UI stage.
            job.timings["technology"] = time.perf_counter() - t

            report = RepositoryReport(
                owner=owner,
                repository=repo_name,
                url=job.github_url,
                default_branch=branch,
                **raw_report["counts"],
                languages=raw_report["languages"],
                technologies=raw_report["technologies"],
                folder_tree=raw_report["folder_tree"],
                files=raw_report["file_summaries"],
                context_files=[path for path, _ in selected],
                context_characters=context_chars,
            )

            self._set(job, stage="llm", progress=72, message=f"Generating explanation with local {self.llm.model}...")
            t = time.perf_counter()
            prompt = build_prompt(
                owner=owner,
                repo_name=repo_name,
                url=job.github_url,
                report=raw_report,
                context_blocks=[block for _, block in selected],
            )
            explanation = self.llm.generate(prompt)
            job.timings["local_llm"] = time.perf_counter() - t

            job.timings["total"] = time.perf_counter() - total_started
            self._set(
                job,
                status="completed",
                stage="complete",
                progress=100,
                message="Repository explanation generated successfully.",
                report=report,
                explanation=explanation,
            )
        except Exception as exc:
            job.timings["total"] = time.perf_counter() - total_started
            self._set(job, status="failed", stage="error", progress=100, message="Analysis failed.", error=str(exc))
        finally:
            if clone_path:
                self.processor.cleanup(clone_path)

    def as_response(self, job_id: str) -> JobStatusResponse:
        job = self.get(job_id)
        if not job:
            raise KeyError(job_id)
        elapsed = time.perf_counter() - job.started_at
        return JobStatusResponse(
            job_id=job.job_id,
            status=job.status,
            stage=job.stage,
            progress=job.progress,
            message=job.message,
            elapsed_seconds=round(elapsed, 2),
            report=job.report,
            explanation=job.explanation,
            error=job.error,
            timings={k: round(v, 2) for k, v in job.timings.items()},
        )
