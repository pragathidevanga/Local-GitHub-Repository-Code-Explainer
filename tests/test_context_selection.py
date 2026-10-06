from backend.file_inspector import InspectedFile
from backend.repository_analyzer import select_context_files


def test_context_is_bounded_and_deduplicated() -> None:
    files = []
    for i in range(100):
        files.append(InspectedFile(
            path=f"src/file_{i}.py",
            category="source",
            language="Python",
            size=5000,
            readable=True,
            sensitive=False,
            binary=False,
            content="print('x')\n" * 1000,
        ))
    files.append(InspectedFile("README.md", "documentation", None, 100, True, False, False, "# Demo"))
    selected, total = select_context_files(files, max_files=10, max_file_size=3000, max_total_chars=10000)
    paths = [p for p, _ in selected]
    assert len(paths) <= 10
    assert len(paths) == len(set(paths))
    assert total <= 10000
    assert "README.md" in paths
