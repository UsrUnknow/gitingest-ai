import subprocess
import sys
import tempfile
from pathlib import Path
import os
import pytest

def test_cli_llm_dry_run_subprocess():
    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = Path(tmpdir) / "main.py"
        file_path.write_text("print('Hello world')\n")
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.abspath("src") + os.pathsep + env.get("PYTHONPATH", "")
        result = subprocess.run([
            sys.executable, "-m", "gitingest.cli", "ai", "gpt-4", tmpdir, "--dry-run"
        ], capture_output=True, text=True, env=env)
        assert result.returncode == 0, f"La commande a échoué (code {result.returncode}) : {result.stderr}\n{result.stdout}"
        assert "[Dry-run] Aucun fichier n'a été écrit." in result.stdout
        assert "main.py" in result.stdout 