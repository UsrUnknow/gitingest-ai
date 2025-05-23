"""Utilitaire pour construire un arbre FileSystemNode à partir d'un chemin racine."""
from pathlib import Path
from gitingest.schemas.filesystem_schema import FileSystemNode, FileSystemNodeType
import os
import fnmatch
try:
    import pathspec
except ImportError:
    pathspec = None

ALWAYS_INCLUDE_PATTERNS = [
    "Dockerfile",
    "docker-compose.yml",
    "docker-compose.*.yml",
    ".env.example",
    ".env.sample",
    "Makefile",
    "Procfile",
    "requirements.txt",
    "pyproject.toml",
    "Pipfile",
    "Pipfile.lock",
    ".gitlab-ci.yml",
    ".github/workflows/*.yml",
    # Pas de wildcard *.json, *.yaml, etc. pour éviter les artefacts générés
]
ALWAYS_INCLUDE_DIRS = [
    ".",  # racine
    ".github",
    "config",
    ".gitlab",
]

def is_in_allowed_dir(rel_path):
    parts = rel_path.split(os.sep)
    if len(parts) == 1:
        return True  # racine
    if parts[0] in ALWAYS_INCLUDE_DIRS:
        return True
    return False

def is_always_included(path, root_path):
    rel_path = os.path.relpath(path, root_path)
    for pattern in ALWAYS_INCLUDE_PATTERNS:
        if fnmatch.fnmatch(rel_path, pattern) or fnmatch.fnmatch(os.path.basename(rel_path), pattern):
            if is_in_allowed_dir(rel_path):
                return True
    return False

def build_filesystem_tree(path: Path, depth: int = 0) -> FileSystemNode:
    if path.is_dir():
        node = FileSystemNode(
            name=path.name,
            type=FileSystemNodeType.DIRECTORY,
            path_str=str(path),
            path=path,
            depth=depth,
        )
        for child in sorted(path.iterdir()):
            node.children.append(build_filesystem_tree(child, depth=depth+1))
        return node
    else:
        size = path.stat().st_size if path.is_file() else 0
        return FileSystemNode(
            name=path.name,
            type=FileSystemNodeType.FILE,
            path_str=str(path),
            path=path,
            size=size,
            depth=depth,
        )

def build_filesystem_tree(root_path):
    """
    Construit l'arborescence du dépôt en excluant les fichiers ignorés par le .gitignore (si présent),
    sinon en excluant les fichiers/dossiers générés courants (caches, artefacts, logs, etc.).
    Retourne un FileSystemNode racine (type DIRECTORY) avec ses enfants.
    """
    gitignore_path = os.path.join(root_path, ".gitignore")
    ignore_patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, "r") as f:
            ignore_patterns = f.read().splitlines()
        spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns) if pathspec else None
    else:
        # Patterns par défaut si pas de .gitignore
        ignore_patterns = [
            "__pycache__", ".mypy_cache", ".pytest_cache", "*.pyc", "*.pyo", "*.pyd", "*.log", "*.tmp", "*.swp", "*.swo",
            "env", ".env", ".venv", "venv", "node_modules", "dist", "build", "*.egg-info", "*.egg", "tmp", "htmlcov", "coverage.*", "*.sqlite3", ".DS_Store"
        ]
        spec = pathspec.PathSpec.from_lines("gitwildmatch", ignore_patterns) if pathspec else None
    def is_ignored(path):
        if not spec:
            return False
        rel_path = os.path.relpath(path, root_path)
        return spec.match_file(rel_path)

    root_path_obj = Path(root_path)
    root_node = FileSystemNode(
        name=root_path_obj.name or str(root_path_obj),
        type=FileSystemNodeType.DIRECTORY,
        path_str=str(root_path_obj),
        path=root_path_obj,
        depth=0,
    )
    # On va indexer les nœuds par chemin pour pouvoir ajouter les enfants facilement
    node_map = {str(root_path_obj): root_node}
    for dirpath, dirnames, filenames in os.walk(root_path):
        parent_path = Path(dirpath)
        rel_parent = os.path.relpath(str(parent_path), root_path)
        parent_depth = 0 if rel_parent == "." else rel_parent.count(os.sep)
        parent_node = node_map.get(str(parent_path))
        # Filtrer les dossiers ignorés
        dirnames[:] = [d for d in dirnames if not is_ignored(os.path.join(dirpath, d)) or is_always_included(os.path.join(dirpath, d), root_path)]
        for dirname in dirnames:
            dpath = Path(os.path.join(dirpath, dirname))
            rel_dpath = os.path.relpath(str(dpath), root_path)
            depth = 0 if rel_dpath == "." else rel_dpath.count(os.sep)
            if any(part in rel_dpath.split(os.sep) for part in ["__pycache__", ".mypy_cache", ".pytest_cache", "env", ".env", ".venv", "venv", "node_modules", "dist", "build", "tmp", "htmlcov"]):
                continue
            node = FileSystemNode(
                name=dpath.name,
                type=FileSystemNodeType.DIRECTORY,
                path_str=str(dpath),
                path=dpath,
                depth=depth,
            )
            node_map[str(dpath)] = node
            if parent_node:
                parent_node.children.append(node)
        for filename in filenames:
            fpath = Path(os.path.join(dirpath, filename))
            # Exclure explicitement les fichiers générés/caches même si allowlist
            if is_ignored(str(fpath)) and not is_always_included(str(fpath), root_path):
                continue
            rel_fpath = os.path.relpath(str(fpath), root_path)
            depth = 0 if rel_fpath == "." else rel_fpath.count(os.sep)
            if any(part in rel_fpath.split(os.sep) for part in ["__pycache__", ".mypy_cache", ".pytest_cache", "env", ".env", ".venv", "venv", "node_modules", "dist", "build", "tmp", "htmlcov"]):
                continue
            size = fpath.stat().st_size if fpath.is_file() else 0
            node = FileSystemNode(
                name=fpath.name,
                type=FileSystemNodeType.FILE,
                path_str=str(fpath),
                path=fpath,
                size=size,
                depth=depth,
            )
            if parent_node:
                parent_node.children.append(node)
    return root_node 