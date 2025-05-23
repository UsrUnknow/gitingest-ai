import os
import json
from pathlib import Path
from click.testing import CliRunner
from gitingest.cli import cli

def create_fake_project(tmp_path):
    (tmp_path / "README.md").write_text("# Universal Project\nL1\nL2\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "MainController.cs").write_text("// C# controller\nLine2\n")
    (tmp_path / "src" / "AppController.js").write_text("// JS controller\nLine2\n")
    (tmp_path / "src" / "entity.py").write_text("# Python entity\nclass Entity: pass\n")
    (tmp_path / "src" / "repository.js").write_text("// JS repo\nfunction repo(){}\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text("def test_app(): pass\n")
    return tmp_path

def test_extract_key_files_cli(tmp_path):
    project_root = create_fake_project(tmp_path)
    runner = CliRunner()
    result = runner.invoke(cli, ["extract-key-files", str(project_root), "--lines", "2"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "readme" in data and "Universal Project" in data["readme"]
    assert "controller" in data and ("controller" in data["controller"] or "Ctrl" in data["controller"])
    assert "entity" in data and ("entity" in data["entity"] or "Entity" in data["entity"])
    assert "repository" in data and ("repo" in data["repository"])
    assert "test" in data and ("test_app" in data["test"]) 