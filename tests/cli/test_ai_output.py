import os
import json
import shutil
import tempfile
import pytest
from click.testing import CliRunner
from gitingest.cli import cli

def create_fake_project(tmp_path, n_files=5, file_size=1000):
    src_dir = tmp_path / "src" / "gitingest"
    src_dir.mkdir(parents=True)
    files = []
    for i in range(n_files):
        f = src_dir / f"file_{i}.py"
        f.write_text("# test file\n" + ("a" * (file_size-10)))
        files.append(f)
    return tmp_path, files

@pytest.mark.parametrize("max_file_size,n_files,file_size", [
    (2000, 5, 1500),   # Doit découper en plusieurs fichiers output
    (10000, 2, 1000),  # Un seul fichier output
])
def test_ai_output_python_content(tmp_path, max_file_size, n_files, file_size):
    # Arrange
    project_dir, files = create_fake_project(tmp_path, n_files=n_files, file_size=file_size)
    runner = CliRunner()
    model = list(__import__('gitingest.config.model_config', fromlist=['MODEL_CONFIGS']).MODEL_CONFIGS.keys())[0]
    # Act
    debug_log = str(project_dir / "debug_gitingest.txt")
    result = runner.invoke(cli, ["ai", model, str(project_dir), "--format", "text", "--log-level", "error", "--debug-log", debug_log])
    # Assert
    assert result.exit_code == 0
    outputs = list(project_dir.glob(f"*_{model}_part*.txt"))
    assert outputs, "Aucun fichier output généré"
    # Vérifie que chaque fichier ne dépasse pas la taille max
    for out in outputs:
        assert out.stat().st_size <= max_file_size + 100, f"{out} dépasse la taille max autorisée"
    # Vérifie que chaque fichier Python est bien présent dans au moins un output
    all_lines = []
    for out in outputs:
        with open(out, "r", encoding="utf-8") as f:
            all_lines.extend(f.readlines())
    found = 0
    for f in files:
        for line in all_lines:
            if f"file_{f.stem.split('_')[-1]}.py" in line:
                found += 1
                break
    assert found == n_files, f"Tous les fichiers Python ne sont pas présents dans l'output IA ({found}/{n_files})"
    # Vérifie la présence du résumé et du tree dans le premier fichier
    with open(outputs[0], "r", encoding="utf-8") as f:
        lines = [json.loads(l) for l in f.readlines() if l.strip()]
    assert any("summary" in l for l in lines), "Résumé absent du premier output"
    assert any("tree" in l for l in lines), "Arborescence absente du premier output" 