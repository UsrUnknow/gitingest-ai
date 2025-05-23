"""Schémas pour la classification des fichiers et le contexte de dépôt pour l'optimisation LLM."""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict

class FileType(Enum):
    """
    Types de fichiers pour la classification dans un dépôt.
    """
    CONFIG = auto()
    DOCUMENTATION = auto()
    SOURCE = auto()
    TEST = auto()
    DATA = auto()
    SCRIPT = auto()
    NOTEBOOK = auto()
    OTHER = auto()

class FileImportance(Enum):
    """
    Niveau d'importance d'un fichier pour l'analyse LLM.
    """
    HIGH = auto()
    MEDIUM = auto()
    LOW = auto()

@dataclass
class FileNode:
    """
    Représente un fichier avec ses métadonnées pour l'analyse LLM.

    Attributs
    ----------
    path : str
        Chemin relatif du fichier dans le dépôt.
    file_type : FileType
        Type de fichier (config, source, documentation, etc.).
    importance : FileImportance
        Importance du fichier pour l'analyse.
    size : int
        Taille du fichier en octets.
    language : Optional[str]
        Langage principal du fichier (si applicable).
    extra : Optional[Dict]
        Métadonnées additionnelles (libre).
    """
    path: str
    file_type: FileType
    importance: FileImportance
    size: int
    language: Optional[str] = None
    extra: Optional[Dict] = field(default_factory=dict)

@dataclass
class RepoContext:
    """
    Contexte complet extrait d'un dépôt pour l'optimisation LLM.

    Attributs
    ----------
    files : List[FileNode]
        Liste des fichiers analysés avec leurs métadonnées.
    repo_name : Optional[str]
        Nom du dépôt (si disponible).
    branch : Optional[str]
        Branche analysée.
    commit : Optional[str]
        Commit analysé.
    extra : Optional[Dict]
        Métadonnées additionnelles (libre).
    """
    files: List[FileNode]
    repo_name: Optional[str] = None
    branch: Optional[str] = None
    commit: Optional[str] = None
    extra: Optional[Dict] = field(default_factory=dict) 