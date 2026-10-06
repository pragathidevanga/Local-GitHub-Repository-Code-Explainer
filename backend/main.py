"""FastAPI backend application service for Local GitHub Repository Code Explainer."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.context_builder import SmartContextBuilder
from backend.github_processor import RepositoryCloner
from backend.llm_service import build_qwen_prompt, check_ollama_status
from backend.models import (
    AnalysisResponse,
    OllamaStatus,
    RepositoryAnalysisRequest,
    TimingMetrics,
)
from backend.repository_analyzer import RepositoryAnalyzer
from backend.utils import Timer, parse_github_url

app = FastAPI(
    title="Local GitHub Repository Code Explainer API",
    description="FastAPI service for repository processing, dynamic file classification, smart context building, and Ollama integration.",
    version="1.0.0",
)

# Enable CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["General"])
def root_endpoint() -> Dict[str, Any]:
    """Root endpoint welcoming users and confirming service status."""
    return {
        "service": "Local GitHub Repository Code Explainer API",
        "status": "running",
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/api/health",
        "analyze_url": "/api/analyze",
    }


@app.get("/api/health", tags=["Health"])
def health_check() -> Dict[str, Any]:
    """Health check endpoint verifying API service operation and Ollama status."""
    ollama_stat = check_ollama_status()
    return {
        "status": "ok",
        "fastapi": True,
        "ollama": {
            "connected": ollama_stat.connected,
            "model_available": ollama_stat.model_available,
            "model_name": ollama_stat.model_name,
            "message": ollama_stat.message,
        },
    }


@app.get("/api/ollama/status", tags=["Ollama"])
def ollama_status() -> OllamaStatus:
    """Check connection and model status for local Ollama instance."""
    return check_ollama_status()


@app.post("/api/analyze", response_model=AnalysisResponse, tags=["Analysis"])
def analyze_repository(request: RepositoryAnalysisRequest) -> AnalysisResponse:
    """Analyze a public GitHub repository and return inventory, smart context, and Qwen prompt.

    Steps:
      1. Validate GitHub URL format immediately.
      2. Shallow clone repository (depth=1).
      3. Scan file inventory once.
      4. Build smart context and Qwen prompt once.
      5. Return response with complete timing metrics.
    """
    total_timer = Timer()
    validation_timer = Timer()
    clone_timer = Timer()
    scan_timer = Timer()
    context_timer = Timer()

    with total_timer:
        # Step 1: Validate URL
        with validation_timer:
            valid, owner, repo_name, normalized_url = parse_github_url(request.url)

        if not valid:
            return AnalysisResponse(
                success=False,
                url=request.url,
                error=normalized_url,  # Contains error message
                timing=TimingMetrics(url_validation_ms=validation_timer.elapsed_ms),
            )

        # Step 2: Clone repository
        with clone_timer:
            clone_success, owner, temp_dir, repo_name, clone_err = RepositoryCloner.clone_to_temp(request.url)

        if not clone_success or not temp_dir:
            return AnalysisResponse(
                success=False,
                url=request.url,
                error=f"Clone failed: {clone_err}",
                timing=TimingMetrics(
                    url_validation_ms=validation_timer.elapsed_ms,
                    clone_ms=clone_timer.elapsed_ms,
                ),
            )

        try:
            # Step 3: Scan inventory
            with scan_timer:
                analyzer = RepositoryAnalyzer(temp_dir, owner, repo_name)
                inventory, file_map = analyzer.analyze()

            if inventory.total_files == 0:
                return AnalysisResponse(
                    success=False,
                    url=request.url,
                    error="Repository is genuinely empty (contains no files).",
                    timing=TimingMetrics(
                        url_validation_ms=validation_timer.elapsed_ms,
                        clone_ms=clone_timer.elapsed_ms,
                        scan_ms=scan_timer.elapsed_ms,
                    ),
                )

            # Step 4: Build smart context & Qwen prompt
            with context_timer:
                context_builder = SmartContextBuilder(temp_dir, file_map)
                smart_context = context_builder.build_context()
                prompt = build_qwen_prompt(inventory, smart_context)

        finally:
            # Clean up temp clone directory safely
            RepositoryCloner.cleanup(temp_dir)

    timing = TimingMetrics(
        url_validation_ms=validation_timer.elapsed_ms,
        clone_ms=clone_timer.elapsed_ms,
        scan_ms=scan_timer.elapsed_ms,
        context_prep_ms=context_timer.elapsed_ms,
        total_ms=total_timer.elapsed_ms,
    )

    return AnalysisResponse(
        success=True,
        url=request.url,
        inventory=inventory,
        smart_context=smart_context,
        prompt=prompt,
        timing=timing,
    )


def process_repository_service(url: str) -> AnalysisResponse:
    """Direct Python service function for Streamlit or internal callers (reuses FastAPI logic)."""
    return analyze_repository(RepositoryAnalysisRequest(url=url))
