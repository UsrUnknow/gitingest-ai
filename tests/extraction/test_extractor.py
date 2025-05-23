import pytest
from gitingest.extraction.extractor import extract_repo_context
from gitingest.schemas.filesystem_schema import FileSystemNode, FileSystemNodeType
from gitingest.config.model_config import LLMModelConfig
from gitingest.schemas import FileType
import tempfile
from pathlib import Path

@pytest.fixture
def dummy_model_config():
    return LLMModelConfig(
        max_tokens=50,  # volontairement petit pour tester le tronquage
        max_file_size=1000,
        important_file_types=[".py"],
        config_files_priority=["pyproject.toml"]
    )

def make_file_node(path, size=10):
    return FileSystemNode(
        name=Path(path).name,
        path=Path(path),
        path_str=str(path),
        type=FileSystemNodeType.FILE,
        size=size,
        children=[],
    )

def make_dir_node(children):
    return FileSystemNode(
        name="fake_repo",
        path=Path("/tmp/fake_repo"),
        path_str="/tmp/fake_repo",
        type=FileSystemNodeType.DIRECTORY,
        size=0,
        children=children,
    )

def test_extract_repo_context_basic(dummy_model_config):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "main.py"
        file_path.write_text("print('Hello world!')\n" * 5)
        node = make_file_node(file_path)
        dir_node = make_dir_node([node])
        ctx = extract_repo_context(dir_node, dummy_model_config, repo_name="fake_repo")
        assert ctx.repo_name == "fake_repo"
        assert len(ctx.files) == 1
        assert ctx.files[0].file_type == FileType.SOURCE
        assert "content" in ctx.files[0].extra


def test_extract_repo_context_truncation(dummy_model_config):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "main.py"
        # Génère un contenu très long
        file_path.write_text("A " * 1000)
        node = make_file_node(file_path)
        dir_node = make_dir_node([node])
        ctx = extract_repo_context(dir_node, dummy_model_config, repo_name="fake_repo")
        assert len(ctx.files) == 1
        assert ctx.files[0].extra.get("truncated", False) is True


def test_extract_repo_context_file_too_big(dummy_model_config):
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "big.py"
        file_path.write_text("A " * 100)
        node = make_file_node(file_path, size=2000)  # taille > max_file_size
        dir_node = make_dir_node([node])
        ctx = extract_repo_context(dir_node, dummy_model_config, repo_name="fake_repo")
        assert len(ctx.files) == 0 