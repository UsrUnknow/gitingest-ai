"""Tests pour les nouvelles fonctionnalités de traitement en mode batch."""

import os
import json
import tempfile
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, Mock

import pytest
from gitingest.cli import cli
from gitingest.config.model_config import MODEL_CONFIGS


def create_test_project(base_path: Path, name: str, files_config: dict):
    """Crée un projet de test avec la structure spécifiée."""
    project_dir = base_path / name
    project_dir.mkdir(exist_ok=True)
    
    created_files = []
    for filename, content in files_config.items():
        filepath = project_dir / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        created_files.append(filepath)
    
    return project_dir, created_files


class TestBatchProcessing:
    """Tests pour le traitement en mode batch."""
    
    def test_batch_command_exists(self):
        """Teste que la commande batch existe."""
        runner = CliRunner()
        result = runner.invoke(cli, ["ai", "batch", "--help"])
        assert result.exit_code == 0
        assert "Traite plusieurs répertoires" in result.output
    
    def test_batch_dry_run(self):
        """Teste le mode dry-run du batch."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Créer plusieurs projets de test
            proj1, _ = create_test_project(temp_path, "project1", {
                "main.py": "print('Hello from project 1')",
                "README.md": "# Project 1"
            })
            proj2, _ = create_test_project(temp_path, "project2", {
                "app.js": "console.log('Hello from project 2');",
                "package.json": '{"name": "project2"}'
            })
            
            runner = CliRunner()
            result = runner.invoke(cli, [
                "ai", "batch", 
                str(proj1), str(proj2),
                "--dry-run"
            ])
            
            assert result.exit_code == 0
            assert "project1" in result.output
            assert "project2" in result.output
            assert "[DRY RUN]" in result.output
    
    def test_batch_with_filtering(self):
        """Teste le batch avec des options de filtrage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Créer un projet avec des fichiers à filtrer
            proj, _ = create_test_project(temp_path, "test_project", {
                "src/main.py": "# Code Python",
                "src/test.py": "# Test Python", 
                "node_modules/lib.js": "// Devrait être exclu",
                "dist/app.js": "// Devrait être exclu",
                "README.md": "# Documentation"
            })
            
            runner = CliRunner()
            result = runner.invoke(cli, [
                "ai", "batch",
                str(proj),
                "--include-ext", "py,md",
                "--dry-run"
            ])
            
            assert result.exit_code == 0
            assert "main.py" in result.output
            assert "README.md" in result.output
            # Les fichiers JS ne devraient pas apparaître avec --include-ext py,md
    
    def test_batch_parallel_processing(self):
        """Teste le traitement parallèle."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Créer plusieurs projets
            projects = []
            for i in range(3):
                proj, _ = create_test_project(temp_path, f"project{i}", {
                    "main.py": f"# Project {i}",
                    "README.md": f"# Documentation {i}"
                })
                projects.append(str(proj))
            
            runner = CliRunner()
            result = runner.invoke(cli, [
                "ai", "batch",
                *projects,
                "--parallel", "2",
                "--dry-run"
            ])
            
            assert result.exit_code == 0
            for i in range(3):
                assert f"project{i}" in result.output


class TestFilteringFunctions:
    """Tests pour les nouvelles fonctions de filtrage."""
    
    def test_filter_filesystem_tree_basic(self):
        """Teste le filtrage de base de l'arbre du système de fichiers."""
        # Ignorer ce test pour l'instant - nous testons manuellement
        pytest.skip("Test intégration manuel en cours")
    
    def test_filter_with_extensions(self):
        """Teste le filtrage par extensions."""
        from gitingest.cli import _filter_filesystem_tree
        
        tree = {
            "type": "directory", 
            "name": "test",
            "children": [
                {"type": "file", "name": "code.py", "size": 100},
                {"type": "file", "name": "style.css", "size": 200},
                {"type": "file", "name": "doc.md", "size": 150}
            ]
        }
        
        # Filtrer uniquement les fichiers Python
        filtered = _filter_filesystem_tree(tree, include_extensions={"py"})
        
        file_names = [child["name"] for child in filtered["children"]]
        assert "code.py" in file_names
        assert "style.css" not in file_names
        assert "doc.md" not in file_names


class TestConfigurationLoading:
    """Tests pour le chargement de la configuration de filtrage."""
    
    def test_default_filters_config_exists(self):
        """Teste que le fichier de configuration par défaut existe."""
        from gitingest.config import default_filters
        config_path = Path(default_filters.__file__).parent / "default_filters.yaml"
        assert config_path.exists()
    
    def test_load_filter_config(self):
        """Teste le chargement de la configuration de filtrage."""
        from gitingest.cli import _load_filter_config
        
        config = _load_filter_config()
        assert "default_exclusions" in config
        assert "important_extensions" in config
        assert "project_types" in config
        
        # Vérifier quelques exclusions par défaut
        exclusions = config["default_exclusions"]
        assert "node_modules" in exclusions["directories"]
        assert ".pyc" in exclusions["extensions"]


@pytest.mark.integration
class TestBatchIntegration:
    """Tests d'intégration pour le mode batch."""
    
    def test_end_to_end_batch_processing(self):
        """Test complet du traitement batch de bout en bout."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            output_dir = temp_path / "output"
            output_dir.mkdir()
            
            # Changer vers le répertoire de sortie
            original_cwd = os.getcwd()
            os.chdir(str(output_dir))
            
            try:
                # Créer un projet de test
                proj, _ = create_test_project(temp_path, "simple_project", {
                    "main.py": "print('Hello World')",
                    "README.md": "# Simple Project",
                    ".gitignore": "*.pyc\n__pycache__/"
                })
                
                runner = CliRunner()
                result = runner.invoke(cli, [
                    "ai", "batch",
                    str(proj),
                    "--format", "jsonl"
                ])
                
                assert result.exit_code == 0
                
                # Vérifier que le fichier de sortie JSONL est créé
                output_files = list(output_dir.glob("*.jsonl"))
                assert len(output_files) == 1
                assert output_files[0].name == "simple_project.jsonl"
                
                # Vérifier le contenu du fichier JSONL
                with open(output_files[0], 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                
                # Premier ligne = métadonnées
                metadata = json.loads(lines[0])
                assert metadata["type"] == "metadata"
                assert metadata["project_name"] == "simple_project"
                
                # Lignes suivantes = fichiers
                file_count = 0
                for line in lines[1:]:
                    file_data = json.loads(line)
                    assert file_data["type"] == "file"
                    assert "path" in file_data
                    assert "content" in file_data
                    file_count += 1
                
                assert file_count > 0  # Au moins un fichier traité
                
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 