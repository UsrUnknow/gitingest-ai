import pytest
from gitingest.classification.classifier import classify_file, determine_importance, should_include_file
from gitingest.schemas import FileType, FileImportance
from gitingest.config.model_config import LLMModelConfig

@pytest.fixture
def dummy_model_config():
    return LLMModelConfig(
        max_tokens=8192,
        max_file_size=1024 * 1024,  # 1 Mo
        important_file_types=[".py", ".md"],
        config_files_priority=["pyproject.toml", "requirements.txt"]
    )

def test_classify_file_config():
    assert classify_file("pyproject.toml") == FileType.CONFIG
    assert classify_file("requirements.txt") == FileType.CONFIG

def test_classify_file_source():
    assert classify_file("main.py") == FileType.SOURCE
    assert classify_file("script.js") == FileType.SOURCE

def test_classify_file_documentation():
    assert classify_file("README.md") == FileType.DOCUMENTATION
    assert classify_file("docs.rst") == FileType.DOCUMENTATION

def test_classify_file_other():
    assert classify_file("image.png") == FileType.OTHER
    assert classify_file("archive.zip") == FileType.OTHER

def test_determine_importance(dummy_model_config):
    assert determine_importance("pyproject.toml", dummy_model_config) == FileImportance.HIGH
    assert determine_importance("main.py", dummy_model_config) == FileImportance.MEDIUM
    assert determine_importance("notes.txt", dummy_model_config) == FileImportance.LOW

def test_should_include_file(dummy_model_config):
    # Important config file
    assert should_include_file("pyproject.toml", dummy_model_config, 100) is True
    # Source file
    assert should_include_file("main.py", dummy_model_config, 100) is True
    # Fichier trop gros
    assert should_include_file("main.py", dummy_model_config, 2 * 1024 * 1024) is False
    # Fichier peu important
    assert should_include_file("notes.txt", dummy_model_config, 100) is False 