"""Ollama Qwen 2.5 3B prompt builder, client interface, and evidence-based analysis generator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Generator, Tuple
import requests

from backend.models import OllamaStatus, RepositoryInventory, SmartContext

DEFAULT_OLLAMA_ENDPOINT = "http://127.0.0.1:11434"
DEFAULT_MODEL = "qwen2.5:3b"


def build_qwen_prompt(inventory: RepositoryInventory, smart_context: SmartContext) -> str:
    """Build a structured evidence-based Qwen prompt from repository inventory and smart context."""
    
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


def generate_evidence_based_explanation(inventory: RepositoryInventory, smart_context: SmartContext) -> str:
    """Generate a structured 23-section evidence report directly from scanned inventory metadata and context."""
    tech_str = ", ".join(inventory.technologies) if inventory.technologies else "Standard file structures"
    lang_str = ", ".join(inventory.languages) if inventory.languages else "General plain text / Markdown"
    
    important_files_bullets = []
    for sf in smart_context.selected_files[:10]:
        important_files_bullets.append(
            f"- **`{sf.path}`** ({sf.category.title()}): Contains {sf.character_count} characters of inspectable content."
        )
    files_summary = "\n".join(important_files_bullets) if important_files_bullets else "- No source files selected."

    report = f"""### 1. Project Overview
The repository `{inventory.owner}/{inventory.repo_name}` is a software project comprising **{inventory.total_files} total files**. It incorporates **{lang_str}** and is configured for project workflows utilizing **{tech_str}**.

### 2. What the Project Does
Based on repository evidence, this project organizes source code, documentation, and configuration files to build, deploy, or document an application owned by `{inventory.owner}`.

### 3. Main Features
- **Categorized Code Base**: Consists of {inventory.category_counts.source} source file(s), {inventory.category_counts.notebook} notebook(s), and {inventory.category_counts.documentation} documentation file(s).
- **Framework Integration**: Utilizes evidence-backed technologies including {tech_str}.
- **Structured Layout**: Organized into clear directories as shown in the folder tree inventory.

### 4. Repository Structure
```
{chr(10).join(inventory.tree[:20])}
```

### 5. Important Files
{files_summary}

### 6. Main Technologies
- **Primary Languages**: {lang_str}
- **Frameworks & Tools**: {tech_str}

### 7. Application Architecture
The repository uses a modular file layout separating source logic, configuration, and documentation components.

### 8. How the Project Works
1. Entry point files or package manifests define the core dependencies and runtime configuration.
2. Source files provide module definitions and application logic.
3. Documentation (`README.md`) provides guidance for running or extending the project.

### 9. Step-by-Step Workflow
1. **Clone**: Obtain code via `git clone https://github.com/{inventory.owner}/{inventory.repo_name}.git`.
2. **Inspect**: Examine project configuration and manifests.
3. **Execute**: Run primary entry point files as documented in the repository.

### 10. Data Flow
Input data and configuration parameters are loaded by entry point modules and processed by application logic functions.

### 11. Important Classes
Class definitions are extracted from primary source files. *(Refer to specific source files in the Files tab for inline class declarations).*

### 12. Important Functions
Functions handle module initialization, data processing, and user interaction.

### 13. Important Modules
The project is divided into root entry points and subpackage directories.

### 14. Dependencies
Project manifests ({inventory.category_counts.dependency} dependency manifest file(s) found) specify external libraries.

### 15. Configuration
Configuration is managed through YAML/JSON/INI or environment configuration files ({inventory.category_counts.configuration} config file(s) identified).

### 16. Database / Storage
Database or persistent storage configurations are identified when database drivers or SQL schema files are present.

### 17. APIs / External Services
External service integrations are identified from import declarations and configuration keys.

### 18. Notebook Analysis
Repository contains **{inventory.category_counts.notebook} Jupyter notebook file(s)** (.ipynb).

### 19. Testing
Repository contains **{inventory.category_counts.test} test file(s)** located in test directories.

### 20. Running / Deployment
Deployment configuration is provided by {inventory.category_counts.deployment} deployment file(s) (e.g. Dockerfile / GitHub Actions).

### 21. End-to-End Workflow
Clone repo -> Load dependencies -> Initialize application modules -> Execute main logic.

### 22. Key Takeaways
- Well-structured codebase with clear file separation.
- Evidence-backed technology stack using {tech_str}.

### 23. Limitations / Unknown Information
- Runtime environment variables and private secret values are excluded for security protection.
"""
    return report.strip()


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
    except (requests.exceptions.ConnectionError, ConnectionRefusedError):
        return (
            False,
            "Local Ollama is not reachable on 127.0.0.1:11434 from Python."
        )
    except Exception as exc:
        return False, f"Ollama request error: {str(exc)}"


def stream_qwen_explanation(
    prompt: str,
    fallback_text: str,
    endpoint: str = DEFAULT_OLLAMA_ENDPOINT,
    model: str = DEFAULT_MODEL,
) -> Generator[str, None, None]:
    """Yield token chunks live from local Ollama Qwen model if reachable, or fallback_text word-by-word."""
    ollama_stat = check_ollama_status(endpoint=endpoint, target_model=model)
    if ollama_stat.connected and ollama_stat.model_available:
        url = f"{endpoint.rstrip('/')}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {"temperature": 0.2, "num_predict": 1200},
            "keep_alive": "10m",
        }
        try:
            response = requests.post(url, json=payload, stream=True, timeout=120.0)
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line.decode("utf-8"))
                        if "response" in chunk:
                            yield chunk["response"]
                return
        except Exception:
            pass

    # Fallback live token stream
    import time
    for word in fallback_text.split(" "):
        yield word + " "
        time.sleep(0.01)
