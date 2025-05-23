"""Formateurs pour structurer le contexte extrait d'un dépôt dans différents formats adaptés aux LLM."""

import json
from typing import Literal, Optional
from gitingest.schemas import RepoContext, FileNode, FileType, FileImportance


def format_repo_context(
    context: RepoContext,
    format: Literal["markdown", "json", "text"] = "markdown",
    markdown_options: Optional[dict] = None,
) -> str:
    """
    Formate le contexte extrait dans le format souhaité (Markdown, JSON, texte brut).

    Paramètres
    ----------
    context : RepoContext
        Contexte extrait à formater.
    format : str
        Format de sortie ('markdown', 'json', 'text').
    markdown_options : dict, optional
        Options de personnalisation pour le format Markdown.

    Retourne
    -------
    str
        Contexte formaté.
    """
    if format == "markdown":
        return format_repo_context_markdown(context, options=markdown_options or {})
    elif format == "json":
        return format_repo_context_json(context)
    elif format == "text":
        return format_repo_context_text(context)
    else:
        raise ValueError(f"Format inconnu : {format}")


def format_repo_context_markdown(context: RepoContext, options: Optional[dict] = None) -> str:
    """
    Formate le contexte extrait en Markdown optimisé pour l'ingestion LLM.

    Paramètres
    ----------
    context : RepoContext
        Contexte extrait à formater.
    options : dict, optional
        Options de personnalisation (ex : inclure/exclure certains types de fichiers).

    Retourne
    -------
    str
        Contexte formaté en Markdown.
    """
    options = options or {}
    include_types = options.get("include_types", None)  # Liste de FileType à inclure
    show_metadata = options.get("show_metadata", True)
    show_content = options.get("show_content", True)
    max_files = options.get("max_files", None)

    lines = []
    if context.repo_name:
        lines.append(f"# Dépôt : {context.repo_name}")
    if context.branch:
        lines.append(f"**Branche** : `{context.branch}`")
    if context.commit:
        lines.append(f"**Commit** : `{context.commit}`")
    lines.append("")
    lines.append(f"## Fichiers extraits ({len(context.files)})")
    lines.append("")
    files = context.files[:max_files] if max_files else context.files
    for file in files:
        if include_types and file.file_type not in include_types:
            continue
        lines.append(f"### `{file.path}`")
        if show_metadata:
            lines.append(f"- Type : **{file.file_type.name}**")
            lines.append(f"- Importance : **{file.importance.name}**")
            lines.append(f"- Taille : {file.size} octets")
            if file.language:
                lines.append(f"- Langage : {file.language}")
            if file.extra and file.extra.get("truncated"):
                lines.append(f"- **Contenu tronqué pour respecter la limite de tokens**")
        if show_content:
            content = file.extra["content"] if file.extra and "content" in file.extra else "[Contenu non disponible]"
            lines.append(f"```{file.language or ''}\n{content}\n```")
        lines.append("")
    if context.extra and context.extra.get("total_tokens"):
        lines.append(f"> **Total estimé de tokens : {context.extra['total_tokens']}**")
    return "\n".join(lines)


def format_repo_context_json(context: RepoContext) -> str:
    """
    Formate le contexte extrait en JSON.

    Paramètres
    ----------
    context : RepoContext
        Contexte extrait à formater.

    Retourne
    -------
    str
        Contexte formaté en JSON.
    """
    def file_to_dict(file: FileNode):
        return {
            "path": file.path,
            "file_type": file.file_type.name,
            "importance": file.importance.name,
            "size": file.size,
            "language": file.language,
            "extra": file.extra,
        }
    data = {
        "repo_name": context.repo_name,
        "branch": context.branch,
        "commit": context.commit,
        "files": [file_to_dict(f) for f in context.files],
        "extra": context.extra,
    }
    return json.dumps(data, ensure_ascii=False, indent=2)


def format_repo_context_text(context: RepoContext) -> str:
    """
    Formate le contexte extrait en texte brut.

    Paramètres
    ----------
    context : RepoContext
        Contexte extrait à formater.

    Retourne
    -------
    str
        Contexte formaté en texte brut.
    """
    lines = []
    if context.repo_name:
        lines.append(f"Dépôt : {context.repo_name}")
    if context.branch:
        lines.append(f"Branche : {context.branch}")
    if context.commit:
        lines.append(f"Commit : {context.commit}")
    lines.append("")
    for file in context.files:
        lines.append(f"Fichier : {file.path} | Type : {file.file_type.name} | Importance : {file.importance.name} | Taille : {file.size} octets")
        if file.language:
            lines.append(f"Langage : {file.language}")
        if file.extra and file.extra.get("truncated"):
            lines.append(f"[Contenu tronqué]")
        content = file.extra["content"] if file.extra and "content" in file.extra else "[Contenu non disponible]"
        lines.append(content)
        lines.append("")
    if context.extra and context.extra.get("total_tokens"):
        lines.append(f"Total estimé de tokens : {context.extra['total_tokens']}")
    return "\n".join(lines) 