from __future__ import annotations

from typing import Any, Literal
from pydantic import BaseModel, Field


class AnalyzeRequest(BaseModel):
    github_url: str = Field(min_length=1, max_length=500)


class FileAnalysis(BaseModel):
    path: str
    category: str
    language: str | None = None
    size: int
    readable: bool = False
    truncated: bool = False
    summary: str | None = None


class RepositoryReport(BaseModel):
    owner: str
    repository: str
    url: str
    default_branch: str | None = None
    total_files: int
    source_files: int
    notebook_files: int
    documentation_files: int
    configuration_files: int
    data_schema_files: int
    test_files: int
    asset_files: int
    binary_files: int
    unknown_text_files: int
    languages: dict[str, int]
    technologies: list[str]
    folder_tree: list[str]
    files: list[FileAnalysis]
    context_files: list[str]
    context_characters: int


class AnalyzeQueuedResponse(BaseModel):
    success: bool = True
    job_id: str
    status: Literal["queued"] = "queued"
    message: str


class JobStatusResponse(BaseModel):
    success: bool = True
    job_id: str
    status: Literal["queued", "running", "completed", "failed"]
    stage: str
    progress: int
    message: str
    elapsed_seconds: float
    report: RepositoryReport | None = None
    explanation: str | None = None
    error: str | None = None
    timings: dict[str, float] = Field(default_factory=dict)


class RootResponse(BaseModel):
    status: str
    message: str
    llm_model: str
    llm_base_url: str
