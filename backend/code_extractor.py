"""Intelligent code excerpting and structural extraction for large files."""

from __future__ import annotations

import re
from pathlib import Path


def excerpt_large_file(content: str, max_chars: int = 20000) -> Tuple[str, bool]:
    """Excerpt large file content preserving imports, declarations, classes, and main logic.

    Args:
        content: Full text content of the file.
        max_chars: Maximum character budget allowed for this file in model context.

    Returns:
        Tuple of (excerpted_content, was_truncated)
    """
    if len(content) <= max_chars:
        return content, False

    lines = content.splitlines()

    # If small number of lines, slice directly
    if len(lines) <= 200:
        truncated_str = "\n".join(lines[:150]) + "\n\n... [TRUNCATED FOR CONTEXT] ...\n"
        return truncated_str[:max_chars], True

    head_lines = lines[:80]
    tail_lines = lines[-40:]

    # Search middle lines for class and function signatures
    middle_lines = lines[80:-40]
    important_middle = []

    sig_pattern = re.compile(
        r"^\s*(class\s+|def\s+|function\s+|async\s+def\s+|public\s+class\s+|export\s+default\s+|export\s+function|struct\s+|interface\s+|enum\s+)",
        re.IGNORECASE,
    )

    for line in middle_lines:
        if sig_pattern.match(line):
            important_middle.append(line)
            if len(important_middle) >= 40:
                break

    excerpt_blocks = [
        "\n".join(head_lines),
        "\n... [TRUNCATED FOR CONTEXT - KEY DECLARATIONS FROM MIDDLE SECTION] ...",
        "\n".join(important_middle),
        "\n... [TRUNCATED FOR CONTEXT - END OF FILE SECTION] ...",
        "\n".join(tail_lines),
    ]

    result = "\n".join(excerpt_blocks)
    if len(result) > max_chars:
        result = result[:max_chars] + "\n... [TRUNCATED FOR CONTEXT] ..."

    return result, True
