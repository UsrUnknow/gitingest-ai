import pytest
from pathlib import Path
from gitingest.utils.key_file_detection import find_key_files, extract_head_lines, generate_extraction_report

def create_fake_project(tmp_path):
    # Crée une structure de projet minimale avec des fichiers clés
    (tmp_path / "README.md").write_text("# Mon projet\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "DF2.Api").mkdir(parents=True)
    (tmp_path / "src" / "DF2.Api" / "Controllers").mkdir(parents=True)
    (tmp_path / "src" / "DF2.Api" / "Controllers" / "OperatorsController.cs").write_text("// controller\n")
    (tmp_path / "src" / "DF2.Domain").mkdir(parents=True)
    (tmp_path / "src" / "DF2.Domain" / "Entities").mkdir(parents=True)
    (tmp_path / "src" / "DF2.Domain" / "Entities" / "Operator.cs").write_text("// entity\n")
    (tmp_path / "src" / "DF2.Infrastructure").mkdir(parents=True)
    (tmp_path / "src" / "DF2.Infrastructure" / "Repositories").mkdir(parents=True)
    (tmp_path / "src" / "DF2.Infrastructure" / "Repositories" / "InMemoryOperatorRepository.cs").write_text("// repo\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "DF2.Domain.Tests").mkdir(parents=True)
    (tmp_path / "tests" / "DF2.Domain.Tests" / "OperatorTests.cs").write_text("// test\n")
    return tmp_path

def test_find_key_files(tmp_path):
    project_root = create_fake_project(tmp_path)
    key_files = find_key_files(project_root)
    assert key_files["readme"] is not None and key_files["readme"].name == "README.md"
    assert key_files["controller"] is not None and "OperatorsController.cs" in str(key_files["controller"])
    assert key_files["entity"] is not None and "Operator.cs" in str(key_files["entity"])
    assert key_files["repository"] is not None and "InMemoryOperatorRepository.cs" in str(key_files["repository"])
    assert key_files["test"] is not None and "OperatorTests.cs" in str(key_files["test"])

def test_extract_head_lines(tmp_path):
    file = tmp_path / "sample.txt"
    content = """Ligne 1\nLigne 2\nLigne 3\nLigne 4\nLigne 5\n"""
    file.write_text(content)
    extrait = extract_head_lines(file, n=3)
    assert extrait == "Ligne 1\nLigne 2\nLigne 3\n"

def test_generate_extraction_report(tmp_path):
    # Crée un projet mixte avec des fichiers Python, JS, C#
    (tmp_path / "README.md").write_text("# Projet universel\nLigne 2\nLigne 3\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "MainController.cs").write_text("// C# controller\nLine2\n")
    (tmp_path / "src" / "AppController.js").write_text("// JS controller\nLine2\n")
    (tmp_path / "src" / "entity.py").write_text("# Python entity\nclass Entity: pass\n")
    (tmp_path / "src" / "repository.js").write_text("// JS repo\nfunction repo(){}\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_app.py").write_text("def test_app(): pass\n")
    # On détecte les fichiers clés
    key_files = find_key_files(tmp_path)
    report = generate_extraction_report(key_files, n_lines=2)
    assert "# Projet universel" in report["readme"]
    assert ("// C# controller" in report["controller"] or "// JS controller" in report["controller"])
    assert ("# Python entity" in report["entity"] or "Entity" in report["entity"])
    assert ("repo" in report["repository"])
    assert ("test_app" in report["test"]) 