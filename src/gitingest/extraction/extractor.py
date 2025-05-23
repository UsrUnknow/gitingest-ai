"""Extraction intelligente du contexte de dépôt pour l'optimisation LLM."""

import os
from pathlib import Path
from typing import List, Optional
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import time

from gitingest.schemas.filesystem_schema import FileSystemNode, FileSystemNodeType
from gitingest.classification.classifier import classify_file, determine_importance, should_include_file
from gitingest.schemas import FileNode, RepoContext, FileType, FileImportance
from gitingest.config.model_config import LLMModelConfig
from gitingest.utils.tokens import count_tokens, truncate_content
from gitingest.utils.exceptions import UnreadableFileError, BinaryFileIgnored
from gitingest.utils.logging_utils import logger


def _gather_files(node: FileSystemNode, model_config: LLMModelConfig) -> List[FileNode]:
    """
    Parcourt récursivement le FileSystemNode et retourne une liste de FileNode classés et typés.

    Paramètres
    ----------
    node : FileSystemNode
        Nœud racine ou courant du système de fichiers.
    model_config : LLMModelConfig
        Configuration du modèle LLM.

    Retourne
    -------
    List[FileNode]
        Liste des fichiers typés et classés.
    """
    files: List[FileNode] = []
    if node.type == FileSystemNodeType.FILE:
        # Inclure tous les fichiers pertinents, sans limite de taille
        ftype = classify_file(node.path_str)
        importance = determine_importance(node.path_str, model_config)
        files.append(
            FileNode(
                path=node.path_str,
                file_type=ftype,
                importance=importance,
                size=node.size,
                language=node.path.suffix.lstrip(".") if node.path.suffix else None,
            )
        )
    elif node.type == FileSystemNodeType.DIRECTORY:
        for child in node.children:
            files.extend(_gather_files(child, model_config))
    return files


def extract_repo_context(
    root_node: FileSystemNode,
    model_config: LLMModelConfig,
    repo_name: Optional[str] = None,
    branch: Optional[str] = None,
    commit: Optional[str] = None,
) -> RepoContext:
    """
    Extrait un contexte pertinent du dépôt en priorisant les fichiers importants et en respectant la limite de tokens.

    Paramètres
    ----------
    root_node : FileSystemNode
        Racine du dépôt à analyser.
    model_config : LLMModelConfig
        Configuration du modèle LLM (limite de tokens, etc.).
    repo_name : str, optional
        Nom du dépôt.
    branch : str, optional
        Branche analysée.
    commit : str, optional
        Commit analysé.

    Retourne
    -------
    RepoContext
        Contexte extrait, prêt à être utilisé pour l'optimisation LLM.
    """
    files = _gather_files(root_node, model_config)
    # Priorisation : config > doc > source > test > data > script > notebook > other
    priority = {
        FileType.CONFIG: 0,
        FileType.DOCUMENTATION: 1,
        FileType.SOURCE: 2,
        FileType.TEST: 3,
        FileType.DATA: 4,
        FileType.SCRIPT: 5,
        FileType.NOTEBOOK: 6,
        FileType.OTHER: 7,
    }
    files.sort(key=lambda f: (priority.get(f.file_type, 99), f.importance.value, -f.size))

    def _read_file_content(file):
        try:
            with open(file.path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return file, content, None
        except Exception as e:
            return file, None, str(e)

    errors = []
    results = []
    start = time.time()
    with ThreadPoolExecutor(max_workers=8) as executor:
        with tqdm(total=len(files), desc="Lecture des fichiers", miniters=1, mininterval=0, leave=True) as pbar:
            for file, content, err in executor.map(_read_file_content, files):
                if err:
                    tqdm.write(f"[ERREUR] {getattr(file, 'path', file)}: {err}")
                    errors.append((getattr(file, 'path', file), err))
                else:
                    file.extra = getattr(file, "extra", {}) or {}
                    file.extra["content"] = content
                    results.append(file)
                pbar.update(1)
    elapsed = time.time() - start
    tqdm.write(f"Lecture terminée en {elapsed:.2f}s, {len(errors)} erreurs.")
    return RepoContext(
        files=results,
        repo_name=repo_name,
        branch=branch,
        commit=commit,
        extra={"read_errors": errors, "read_time": elapsed}
    ) 