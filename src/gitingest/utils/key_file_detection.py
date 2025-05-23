"""
Détection automatique des fichiers clés d'un projet (README, contrôleur, entité, repository, test, etc.).
"""
from pathlib import Path
from typing import Dict, Optional
import fnmatch

def find_key_files(root_path: Path) -> Dict[str, Optional[Path]]:
    """
    Parcourt l'arborescence à partir de root_path et retourne un dict des fichiers clés détectés.
    Ex : {"readme": Path(...), "controller": Path(...), ...}
    """
    patterns = {
        "readme": ["README.md", "README.MD", "readme.md"],
        "controller": [
            "*Controller.*", "*controller.*", "*Ctrl.*", "*ctrl.*",
            "*Controller.cs", "*Controller.js", "*Controller.ts", "*Controller.java", "*Controller.go", "*Controller.py",
            "*controller.cs", "*controller.js", "*controller.ts", "*controller.java", "*controller.go", "*controller.py"
        ],
        "entity": [
            "*Entity.*", "*entity.*", "*Model.*", "*model.*",
            "*Entity.cs", "*Entity.js", "*Entity.ts", "*Entity.java", "*Entity.go", "*Entity.py",
            "*entity.cs", "*entity.js", "*entity.ts", "*entity.java", "*entity.go", "*entity.py",
            "*Model.cs", "*Model.js", "*Model.ts", "*Model.java", "*Model.go", "*Model.py",
            "*model.cs", "*model.js", "*model.ts", "*model.java", "*model.go", "*model.py"
        ],
        "repository": [
            "*Repository.*", "*repository.*", "*Repo.*", "*repo.*",
            "*Repository.cs", "*Repository.js", "*Repository.ts", "*Repository.java", "*Repository.go", "*Repository.py",
            "*repository.cs", "*repository.js", "*repository.ts", "*repository.java", "*repository.go", "*repository.py",
            "*Repo.cs", "*Repo.js", "*Repo.ts", "*Repo.java", "*Repo.go", "*Repo.py",
            "*repo.cs", "*repo.js", "*repo.ts", "*repo.java", "*repo.go", "*repo.py"
        ],
        "test": [
            "*Test*.*", "*test*.*", "test_*.*", "*_test.*",
            "*Test*.cs", "*Test*.js", "*Test*.ts", "*Test*.java", "*Test*.go", "*Test*.py",
            "*test*.cs", "*test*.js", "*test*.ts", "*test*.java", "*test*.go", "*test*.py",
            "test_*.cs", "test_*.js", "test_*.ts", "test_*.java", "test_*.go", "test_*.py",
            "*_test.cs", "*_test.js", "*_test.ts", "*_test.java", "*_test.go", "*_test.py"
        ],
    }
    result = {k: None for k in patterns}
    for ptype, pats in patterns.items():
        for path in root_path.rglob("*"):
            if not path.is_file():
                continue
            for pat in pats:
                if fnmatch.fnmatch(path.name, pat):
                    result[ptype] = path
                    break
            if result[ptype]:
                break
    if result["entity"] is None:
        for path in root_path.rglob("*"):
            if not path.is_file():
                continue
            parents = [p.name.lower() for p in path.parents]
            if any(d in parents for d in ["entities", "models", "domain"]):
                result["entity"] = path
                break
    return result 

def extract_head_lines(file_path: Path, n: int = 40) -> str:
    """
    Extrait les n premières lignes du fichier file_path et les retourne sous forme de chaîne.
    """
    try:
        with file_path.open("r", encoding="utf-8") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= n:
                    break
                lines.append(line)
        return "".join(lines)
    except Exception:
        return "" 

def generate_extraction_report(key_files: Dict[str, Optional[Path]], n_lines: int = 40) -> Dict[str, str]:
    """
    Pour chaque type de fichier clé détecté, extrait les n premières lignes et retourne un dict {type: extrait}.
    """
    report = {}
    for k, path in key_files.items():
        if path is not None:
            report[k] = extract_head_lines(path, n=n_lines)
        else:
            report[k] = ""
    return report 