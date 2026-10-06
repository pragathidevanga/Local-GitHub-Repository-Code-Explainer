"""Pydantic data schemas for request, response, and domain models."""

from __future__ import annotations

from typing import Dict, List, Optional
from pydantic import BaseModel, Field, HttpUrl


class RepositoryAnalysisRequest(BaseModel):
    """Input payload containing target GitHub repository URL."""
    url: str = Field(..., description="HTTPS URL of public GitHub repository")


class FileInfo(BaseModel):
    """Metadata and inspection info for a single repository file."""
    path: str
    category: str
    size_bytes: int
    extension: str
    is_sensitive: bool = False
    priority_score: int = 0
    content_preview: Optional[str] = None


class CategoryCounts(BaseModel):
    """Categorized file counts across the full repository inventory."""
    source: int = 0
    notebook: int = 0
    documentation: int = 0
    configuration: int = 0
    dependency: int = 0
    web: int = 0
    data_schema: int = 0
    test: int = 0
    deployment: int = 0
    binary: int = 0
    unknown_text: int = 0


class RepositoryInventory(BaseModel):
    """Complete structural inventory of analyzed repository."""
    owner: str
    repo_name: str
    total_files: int
    category_counts: CategoryCounts
    languages: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    tree: List[str] = Field(default_factory=list)
    important_files: List[str] = Field(default_factory=list)
    sensitive_files_found: List[str] = Field(default_factory=list)


class SelectedFileContext(BaseModel):
    """Single file snippet selected for LLM model context."""
    path: str
    category: str
    character_count: int
    is_truncated: bool
    content: str


class SmartContext(BaseModel):
    """Optimized smart context built for low-latency LLM prompt."""
    selected_files: List[SelectedFileContext] = Field(default_factory=list)
    total_characters: int = 0
    file_count: int = 0


class TimingMetrics(BaseModel):
    """Detailed performance timings in milliseconds."""
    url_validation_ms: float = 0.0
    clone_ms: float = 0.0
    scan_ms: float = 0.0
    context_prep_ms: float = 0.0
    ollama_ms: float = 0.0
    total_ms: float = 0.0


class AnalysisResponse(BaseModel):
    """Complete backend API response schema."""
    success: bool
    url: str
    inventory: Optional[RepositoryInventory] = None
    smart_context: Optional[SmartContext] = None
    prompt: Optional[str] = None
    timing: TimingMetrics = Field(default_factory=TimingMetrics)
    error: Optional[str] = None


class OllamaStatus(BaseModel):
    """Status report for local Ollama instance and Qwen model."""
    connected: bool = False
    model_available: bool = False
    model_name: str = "qwen2.5:3b"
    message: str = ""
    endpoint: str = "http://127.0.0.1:11434"
