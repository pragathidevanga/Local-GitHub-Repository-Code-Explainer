"""Ollama Qwen 2.5 3B prompt builder and Python client interface."""

from __future__ import annotations

import json
from typing import Dict, Generator, Tuple
import requests

from backend.models import OllamaStatus, RepositoryInventory, SmartContext

DEFAULT_OLLAMA_ENDPOINT = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:3b"


def build_qwen_prompt(inventory: RepositoryInventory, smart_context: SmartContext) -> str:
    """Build a structured evidence-based Qwen prompt from repository inventory and smart context."""
    
    # Format selected file snippets
    file_snippets_text = []
    for sf in smart_context.selected_files:
        trunc_tag = " [TRUNCATED FOR CONTEXT]" if sf.is_truncated else ""
        file_snippets_text.append(
            f"========================================================\n"
            f"FILE: {sf.path} ({sf.category.upper()}){trunc_tag}\n"
            f"========================================================\n"
            f"{sf.content}\n"
        )

    all_snippets = "\n".join(file_snippets_text)

    prompt = f"""You are an expert AI software architect explaining a real GitHub repository to a beginner student.

CRITICAL INSTRUCTIONS:
- Use ONLY the supplied repository evidence below.
- Do NOT invent files, frameworks, technologies, databases, APIs, functions, classes, features, commands, workflows, or architecture.
- Explain the repository in detailed, simple, beginner-friendly language.
- If information cannot be determined from the supplied repository evidence, say so explicitly: "This could not be determined from the available repository content."

========================================================
REPOSITORY METADATA & INVENTORY EVIDENCE
========================================================
Repository Owner: {inventory.owner}
Repository Name: {inventory.repo_name}
Total Files: {inventory.total_files}
File Category Counts:
  - Source Code Files: {inventory.category_counts.source}
  - Notebook Files (.ipynb): {inventory.category_counts.notebook}
  - Documentation Files: {inventory.category_counts.documentation}
  - Configuration Files: {inventory.category_counts.configuration}
  - Dependency Manifests: {inventory.category_counts.dependency}
  - Web Files (HTML/CSS): {inventory.category_counts.web}
  - Data / Schema Files: {inventory.category_counts.data_schema}
  - Test Files: {inventory.category_counts.test}
  - Deployment / CI/CD Files: {inventory.category_counts.deployment}
  - Binary / Asset Files: {inventory.category_counts.binary}
  - Unknown Readable Text Files: {inventory.category_counts.unknown_text}

Detected Languages: {', '.join(inventory.languages) if inventory.languages else 'None explicitly identified'}
Detected Technologies / Frameworks: {', '.join(inventory.technologies) if inventory.technologies else 'None explicitly identified'}

Folder Structure Preview:
{chr(10).join(inventory.tree[:30])}

========================================================
SELECTED REPOSITORY CODE & CONTENT EVIDENCE ({smart_context.file_count} files selected)
========================================================
{all_snippets}

========================================================
REQUIRED DETAILED EXPLANATION FORMAT
========================================================
Please generate a detailed, beginner-friendly, evidence-based explanation formatted under the following numbered headers:

1. Project Overview
2. What the Project Does
3. Main Features
4. Repository Structure
5. Important Files (Explain filename, purpose, key code/classes/functions, and role)
6. Main Technologies
7. Application Architecture
8. How the Project Works
9. Step-by-Step Workflow
10. Data Flow
11. Important Classes
12. Important Functions
13. Important Modules
14. Dependencies
15. Configuration
16. Database / Storage
17. APIs / External Services
18. Notebook Analysis
19. Testing
20. Running / Deployment
21. End-to-End Workflow
22. Key Takeaways
23. Limitations / Unknown Information

Generate the explanation now using strictly the evidence provided above:"""

    return prompt


def check_ollama_status(endpoint: str = DEFAULT_OLLAMA_ENDPOINT, target_model: str = DEFAULT_MODEL) -> OllamaStatus:
    """Check connectivity to local Ollama server and verify Qwen model availability."""
    try:
        resp = requests.get(f"{endpoint.rstrip('/')}/api/tags", timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            models = data.get("models", [])
            model_names = [m.get("name", "").lower() for m in models]

            target_found = any(target_model.lower() in m_name for m_name in model_names)

            if target_found:
                return OllamaStatus(
                    connected=True,
                    model_available=True,
                    model_name=target_model,
                    message=f"Local Ollama connected. Model '{target_model}' is available.",
                    endpoint=endpoint,
                )
            else:
                return OllamaStatus(
                    connected=True,
                    model_available=False,
                    model_name=target_model,
                    message=f"Local Ollama is running, but '{target_model}' is not installed.",
                    endpoint=endpoint,
                )
        else:
            return OllamaStatus(
                connected=False,
                model_available=False,
                model_name=target_model,
                message=f"Ollama returned HTTP status {resp.status_code}.",
                endpoint=endpoint,
            )
    except Exception as exc:
        return OllamaStatus(
            connected=False,
            model_available=False,
            model_name=target_model,
            message=f"Cannot connect to local Ollama at {endpoint}. Ensure Ollama is running.",
            endpoint=endpoint,
        )


def generate_with_ollama_local(
    prompt: str,
    endpoint: str = DEFAULT_OLLAMA_ENDPOINT,
    model: str = DEFAULT_MODEL,
    stream: bool = True,
) -> Tuple[bool, str]:
    """Execute local Qwen model inference via Ollama HTTP API (for server-side or CLI testing)."""
    url = f"{endpoint.rstrip('/')}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream,
        "options": {
            "temperature": 0.2,
            "num_predict": 850,
        },
        "keep_alive": "10m",
    }

    try:
        response = requests.post(url, json=payload, stream=stream, timeout=120.0)
        if response.status_code == 200:
            full_response = []
            if stream:
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        if "response" in chunk:
                            full_response.append(chunk["response"])
                return True, "".join(full_response)
            else:
                result = response.json()
                return True, result.get("response", "")
        else:
            return False, f"Ollama HTTP error {response.status_code}: {response.text}"
    except Exception as exc:
        return False, f"Ollama request failed: {str(exc)}"
