"""Fonctions de classification et d'évaluation d'importance des fichiers pour l'optimisation LLM."""

import os
from typing import Optional, cast, Any, List
from gitingest.schemas import FileType, FileImportance
from gitingest.config.model_config import LLMModelConfig, IMPORTANT_FILE_TYPES, CONFIG_FILES_PRIORITY
from gitingest.utils.logging_utils import logger
import yaml
import logging

RULES_YAML = os.path.join(os.path.dirname(__file__), "../config/classification_rules.yaml")

def load_classification_rules():
    logger = logging.getLogger("gitingest.classification")
    if not os.path.exists(RULES_YAML):
        logger.warning(f"Fichier de règles de classification YAML non trouvé : {RULES_YAML}")
        return None
    with open(RULES_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    # Validation des clés attendues
    expected_keys = [
        "config_files", "documentation_exts", "source_exts", "test_patterns",
        "notebook_exts", "script_exts", "data_exts"
    ]
    for key in expected_keys:
        if key not in data or not isinstance(data[key], list):
            logger.warning(f"Clé ou format manquant/invalide dans les règles de classification YAML : '{key}'")
    return data

RULES = load_classification_rules()

def get_str_list(d: dict[str, Any], key: str) -> List[str]:
    val = d.get(key)
    return val if isinstance(val, list) and all(isinstance(x, str) for x in val) else []

def classify_file(path: str) -> FileType:
    """
    Détermine le type d'un fichier à partir de son chemin ou de son nom.

    Paramètres
    ----------
    path : str
        Chemin du fichier à analyser.

    Retourne
    -------
    FileType
        Type de fichier détecté (CONFIG, DOCUMENTATION, SOURCE, etc.).
    """
    filename = os.path.basename(path).lower()
    ext = os.path.splitext(filename)[1]
    if RULES:
        if filename in (RULES.get("config_files") or []):
            return FileType.CONFIG
        if ext in (RULES.get("documentation_exts") or []):
            return FileType.DOCUMENTATION
        if ext in (RULES.get("source_exts") or []):
            return FileType.SOURCE
        if ext in (RULES.get("notebook_exts") or []):
            return FileType.NOTEBOOK
        if ext in (RULES.get("script_exts") or []):
            return FileType.SCRIPT
        if ext in (RULES.get("data_exts") or []):
            return FileType.DATA
        test_patterns = cast(List[str], get_str_list(RULES, "test_patterns") if RULES else [])
        if any(pat in filename for pat in test_patterns):  # type: ignore
            return FileType.TEST
        return FileType.OTHER
    else:
        if filename in CONFIG_FILES_PRIORITY or ext in ('.toml', '.yml', '.yaml', '.json', '.ini', '.cfg', '.env'):
            return FileType.CONFIG
        if filename in ("readme.md", "readme.txt", "license", "changelog", "contributing.md", "code_of_conduct.md") or ext in (".md", ".rst", ".adoc", ".txt"):
            return FileType.DOCUMENTATION
        if ext in (".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c", ".h", ".cs", ".php", ".rb", ".swift", ".kt", ".scala", ".groovy"):
            return FileType.SOURCE
        if ext in (".ipynb", ):
            return FileType.NOTEBOOK
        if ext in (".sh", ".bash", ".zsh", ".ps1", ".psm1", ".bat", ".cmd", ".fish"):
            return FileType.SCRIPT
        if ext in (".csv", ".tsv", ".parquet", ".xls", ".xlsx", ".jsonl", ".db", ".sqlite", ".h5", ".hdf5"):
            return FileType.DATA
        if ext in (".test.js", ".test.ts", ".spec.js", ".spec.ts", ".test.py", ".spec.py", ".test.java", ".spec.java") or "test" in filename or "spec" in filename:
            return FileType.TEST
        return FileType.OTHER


def determine_importance(path: str, model_config: LLMModelConfig) -> FileImportance:
    """
    Évalue l'importance d'un fichier selon la configuration du modèle LLM.

    Paramètres
    ----------
    path : str
        Chemin du fichier à analyser.
    model_config : LLMModelConfig
        Configuration du modèle LLM utilisée.

    Retourne
    -------
    FileImportance
        Niveau d'importance du fichier (HIGH, MEDIUM, LOW).
    """
    filename = os.path.basename(path).lower()
    ext = os.path.splitext(filename)[1]

    if filename in model_config.config_files_priority:
        return FileImportance.HIGH
    if ext in (model_config.important_file_types or []):
        return FileImportance.MEDIUM
    return FileImportance.LOW


def should_include_file(path: str, model_config: LLMModelConfig, size: Optional[int] = None) -> bool:
    """
    Décide si un fichier doit être inclus dans l'extraction selon la config du modèle LLM.

    Paramètres
    ----------
    path : str
        Chemin du fichier à analyser.
    model_config : LLMModelConfig
        Configuration du modèle LLM utilisée.
    size : Optional[int]
        Taille du fichier en octets (si connue).

    Retourne
    -------
    bool
        True si le fichier doit être inclus, False sinon.
    """
    if size is not None and size > model_config.max_file_size:
        return False
    importance = determine_importance(path, model_config)
    return importance != FileImportance.LOW 