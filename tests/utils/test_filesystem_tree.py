import tempfile
from pathlib import Path
from gitingest.utils.filesystem_tree import build_filesystem_tree
from gitingest.schemas.filesystem_schema import FileSystemNodeType

def test_build_filesystem_tree_simple():
    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        (root / "file1.txt").write_text("abc")
        (root / "file2.py").write_text("print('x')")
        subdir = root / "subdir"
        subdir.mkdir()
        (subdir / "file3.md").write_text("doc")
        tree = build_filesystem_tree(root)
        assert tree.type == FileSystemNodeType.DIRECTORY
        assert tree.name == root.name
        assert len(tree.children) == 3  # 2 fichiers + 1 dossier
        files = {c.name: c for c in tree.children}
        assert "file1.txt" in files and files["file1.txt"].type == FileSystemNodeType.FILE
        assert "file2.py" in files and files["file2.py"].type == FileSystemNodeType.FILE
        assert "subdir" in files and files["subdir"].type == FileSystemNodeType.DIRECTORY
        # Vérifie le sous-dossier
        sub = files["subdir"]
        assert len(sub.children) == 1
        assert sub.children[0].name == "file3.md"
        assert sub.children[0].type == FileSystemNodeType.FILE
        assert sub.children[0].size == 3 