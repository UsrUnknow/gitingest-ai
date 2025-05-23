"""
Tests for the `query_ingestion` module.

These tests validate directory scanning, file content extraction, notebook handling, and the overall ingestion logic,
including filtering patterns and subpaths.
"""

import os
import shutil
import tempfile
from pathlib import Path
import pytest

from gitingest.ingestion import ingest_query, apply_gitingest_file
from gitingest.query_parsing import IngestionQuery

@pytest.fixture
def temp_dir(tmp_path):
    # Crée une arborescence de test
    d = tmp_path / "repo"
    d.mkdir()
    (d / "file1.txt").write_text("abc")
    (d / "file2.py").write_text("print('ok')")
    (d / "file3.bin").write_bytes(b"\x00\x01\x02")
    sub = d / "subdir"
    sub.mkdir()
    (sub / "file4.txt").write_text("sub")
    return d

@pytest.fixture
def base_query(temp_dir):
    q = IngestionQuery(
        id="test-id",
        url=None,
        slug="test/test",
        local_path=temp_dir,
        subpath="/",
        type=None,
        branch=None,
        commit=None,
        ignore_patterns=None,
        include_patterns=None,
        max_file_size=1000,
    )
    return q

def test_run_ingest_query(temp_directory: Path, sample_query: IngestionQuery) -> None:
    """
    Test `ingest_query` to ensure it processes the directory and returns expected results.

    Given a directory with .txt and .py files:
    When `ingest_query` is invoked,
    Then it should produce a summary string listing the files analyzed and a combined content string.
    """
    sample_query.local_path = temp_directory
    sample_query.subpath = "/"
    sample_query.type = None

    summary, _, content = ingest_query(sample_query)

    assert "Repository: test_user/test_repo" in summary
    assert "Files analyzed: 8" in summary

    # Check presence of key files in the content
    assert "src/subfile1.txt" in content
    assert "src/subfile2.py" in content
    assert "src/subdir/file_subdir.txt" in content
    assert "src/subdir/file_subdir.py" in content
    assert "file1.txt" in content
    assert "file2.py" in content
    assert "dir1/file_dir1.txt" in content
    assert "dir2/file_dir2.txt" in content


# TODO: Additional tests:
# - Multiple include patterns, e.g. ["*.txt", "*.py"] or ["/src/*", "*.txt"].
# - Edge cases with weird file names or deep subdirectory structures.
# TODO : def test_include_txt_pattern
# TODO : def test_include_nonexistent_extension

def test_include_pattern_txt(base_query):
    # Adapter le pattern pour matcher la structure réelle
    base_query.include_patterns = {"*.txt", "subdir/*.txt"}
    summary, _, content = ingest_query(base_query)
    print("[DEBUG] Contenu retourné:\n", content)
    assert "file1.txt" in content
    assert "file2.py" not in content
    assert "subdir/file4.txt" in content

def test_exclude_pattern_py(base_query):
    base_query.ignore_patterns = {"*.py"}
    summary, _, content = ingest_query(base_query)
    assert "file2.py" not in content
    assert "file1.txt" in content

def test_max_file_size_exclusion(base_query, temp_dir):
    big = temp_dir / "big.txt"
    big.write_text("x" * 2000)
    # Correction : s'assurer que le champ utilisé est bien max_file_size
    base_query.max_file_size = 100
    summary, _, content = ingest_query(base_query)
    # Pour debug : print(content)
    assert "big.txt" not in content

def test_symlink_handling(base_query, temp_dir):
    # Symlink interne
    target = temp_dir / "file1.txt"
    link = temp_dir / "link"
    link.symlink_to(target)
    summary, _, content = ingest_query(base_query)
    assert "link" in content
    # Symlink sortant
    ext = temp_dir.parent / "outside.txt"
    ext.write_text("out")
    outlink = temp_dir / "outlink"
    outlink.symlink_to(ext)
    summary, _, content = ingest_query(base_query)
    assert "outlink" not in content

# Le test de profondeur est désactivé car le champ max_depth n'existe pas dans IngestionQuery
# et la profondeur est gérée globalement par la config.
# def test_depth_limit(base_query, temp_dir):
#     # Crée une arbo profonde
#     deep = temp_dir
#     for i in range(10):
#         deep = deep / f"d{i}"
#         deep.mkdir()
#         (deep / f"f{i}.txt").write_text("x")
#     # base_query.max_depth = 3  # Ce champ n'existe pas
#     summary, tree, content = ingest_query(base_query)
#     # On ne doit pas trouver les fichiers trop profonds
#     assert "f9.txt" not in content
#     assert "f0.txt" in content

def test_file_not_found(base_query):
    base_query.local_path = base_query.local_path / "notfound"
    with pytest.raises(ValueError):
        ingest_query(base_query)

def test_file_empty(tmp_path):
    f = tmp_path / "empty.txt"
    f.write_text("")
    q = IngestionQuery(
        id="test-id",
        url=None,
        slug="test/test",
        local_path=tmp_path,
        subpath="empty.txt",
        type="blob",
        branch=None,
        commit=None,
        ignore_patterns=None,
        include_patterns=None,
        max_file_size=1000,
    )
    with pytest.raises(ValueError):
        ingest_query(q)

def test_apply_gitingest_file(tmp_path):
    d = tmp_path / "repo"
    d.mkdir()
    gitingest = d / ".gitingest"
    gitingest.write_text("""
[config]
ignore_patterns = ["*.py", "*.md"]
""")
    q = IngestionQuery(
        id="test-id",
        url=None,
        slug="test/test",
        local_path=d,
        subpath="/",
        type=None,
        branch=None,
        commit=None,
        ignore_patterns=None,
        include_patterns=None,
        max_file_size=1000,
    )
    apply_gitingest_file(d, q)
    assert "*.py" in q.ignore_patterns
    assert "*.md" in q.ignore_patterns
