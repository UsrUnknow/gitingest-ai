import os
import tempfile
from pathlib import Path
from click.testing import CliRunner
import pytest

from gitingest.cli import cli

def test_cli_llm_command_presence():
    runner = CliRunner()
    result = runner.invoke(cli, ["ai", "--help"])
    assert result.exit_code == 0, f"La commande 'ai --help' a échoué : {result.output}"
    assert "gpt-4" in result.output, "La sous-commande 'gpt-4' n'est pas listée dans 'gitingest ai --help'"
    assert "gpt-4o" in result.output, "La sous-commande 'gpt-4o' n'est pas listée dans 'gitingest ai --help'"

@pytest.mark.parametrize("model_name", ["gpt-4", "gpt-4o"])  # On teste deux modèles
def test_cli_llm_dry_run(model_name):
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        # Crée un fichier factice dans le dossier temporaire
        file_path = Path(tmpdir) / "main.py"
        file_path.write_text("print('Hello world')\n")
        # Appelle la CLI LLM avec --dry-run
        result = runner.invoke(cli, ["ai", model_name, tmpdir, "--dry-run"])
        if result.exit_code != 0:
            print("Sortie CLI :", result.output)
        assert result.exit_code == 0, f"La commande a échoué (code {result.exit_code}) : {result.output}"
        assert "[Dry-run] Aucun fichier n'a été écrit." in result.output
        assert "main.py" in result.output  # Le fichier doit apparaître dans la sortie formatée

def test_cli_llm_audit_option():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "main.py"
        file_path.write_text("print('Hello world')\n")
        result = runner.invoke(cli, ["ai", "gpt-4", tmpdir, "--dry-run", "--audit"])
        assert result.exit_code == 0, f"La commande a échoué (code {result.exit_code}) : {result.output}"
        assert "[Audit] Décisions de classification" in result.output
        assert "main.py" in result.output 