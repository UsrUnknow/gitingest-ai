import pytest
from gitingest.formatting.formatter import format_repo_context
from gitingest.schemas import RepoContext, FileNode, FileType, FileImportance

@pytest.fixture
def minimal_context():
    file1 = FileNode(
        path="main.py",
        file_type=FileType.SOURCE,
        importance=FileImportance.HIGH,
        size=42,
        language="python",
        extra={"content": "print('Hello')", "truncated": False}
    )
    file2 = FileNode(
        path="README.md",
        file_type=FileType.DOCUMENTATION,
        importance=FileImportance.MEDIUM,
        size=12,
        language="markdown",
        extra={"content": "# Doc", "truncated": False}
    )
    return RepoContext(
        files=[file1, file2],
        repo_name="demo",
        branch="main",
        commit="abc123",
        extra={"total_tokens": 123}
    )

def test_format_markdown_basic(minimal_context):
    out = format_repo_context(minimal_context, format="markdown")
    assert "# Dépôt : demo" in out
    assert "main.py" in out and "README.md" in out
    assert "print('Hello')" in out
    assert "# Doc" in out
    assert "Total estimé de tokens" in out

def test_format_markdown_options(minimal_context):
    out = format_repo_context(minimal_context, format="markdown", markdown_options={"max_files": 1, "show_metadata": False, "show_content": True})
    assert out.count("### `") == 1  # Un seul fichier affiché
    assert "Type" not in out  # Pas de métadonnées
    assert "print('Hello')" in out or "# Doc" in out

def test_format_json(minimal_context):
    out = format_repo_context(minimal_context, format="json")
    assert '"repo_name": "demo"' in out
    assert '"files":' in out
    assert '"main.py"' in out
    assert '"README.md"' in out

def test_format_text(minimal_context):
    out = format_repo_context(minimal_context, format="text")
    assert "Dépôt : demo" in out
    assert "main.py" in out and "README.md" in out
    assert "print('Hello')" in out
    assert "# Doc" in out 