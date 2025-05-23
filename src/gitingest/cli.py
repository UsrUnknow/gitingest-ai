"""Command-line interface for the Gitingest package."""

# pylint: disable=no-value-for-parameter

import asyncio
from typing import Optional, Tuple

import click
import sys
from pathlib import Path
from gitingest.schemas.filesystem_schema import FileSystemNode, FileSystemNodeType
from gitingest.extraction.extractor import extract_repo_context
from gitingest.config.model_config import MODEL_CONFIGS
from gitingest.formatting.formatter import format_repo_context
from gitingest.utils.filesystem_tree import build_filesystem_tree
from gitingest.utils.exceptions import InvalidConfigError, UnreadableFileError, BinaryFileIgnored

from gitingest.config import MAX_FILE_SIZE, OUTPUT_FILE_NAME
from gitingest.entrypoint import ingest_async
from tqdm import tqdm
import time

def create_cli():
    @click.group()
    def cli():
        """Gitingest CLI (analyse classique et optimisation LLM)"""
        pass

    @cli.group()
    def ai():
        """Extraction optimisée pour LLM (GPT, Claude, Gemini, etc.)"""
        pass

    def make_model_command(model_name):
        @ai.command(name=model_name)
        @click.argument("source", type=str, default=".")
        @click.option("--format", "-f", default="markdown", show_default=True, type=click.Choice(["markdown", "json", "text"]), help="Format de sortie du contexte optimisé.")
        @click.option("--output", "-o", default=None, help="Chemin du fichier de sortie (par défaut: stdout)")
        @click.option("--max-files", default=None, type=int, help="Nombre maximal de fichiers à inclure dans le contexte.")
        @click.option("--show-metadata/--no-metadata", default=True, help="Afficher les métadonnées des fichiers dans le format Markdown.")
        @click.option("--show-content/--no-content", default=True, help="Afficher le contenu des fichiers dans le format Markdown.")
        @click.option("--audit", is_flag=True, help="Afficher un rapport détaillé des décisions de classification et d'extraction.")
        @click.option("--dry-run", is_flag=True, help="Simuler l'extraction sans écrire de fichier.")
        @click.option("--log-level", default="info", type=click.Choice(["debug", "info", "warning", "error"]), help="Niveau de log à utiliser.")
        @click.option("--export-decisions", default=None, help="Chemin d'export des décisions de classification (JSON).")
        @click.option("--debug-log", default=None, help="Chemin du fichier de log debug (optionnel)")
        @click.option('--no-progress', is_flag=True, default=False, help='Désactive la barre de progression.')
        def model_command(source, format, output, max_files, show_metadata, show_content, audit, dry_run, log_level, export_decisions, debug_log, no_progress, _model_name=model_name):
            """
            Extraction optimisée pour le modèle LLM preset : {model}

            SOURCE : chemin du dossier racine du dépôt à analyser (par défaut: .)

            Exemples d'utilisation :
              gitingest ai {model} ./mon-projet --dry-run
              gitingest ai {model} ./src --format json --output contexte.json

            Options principales :
              --format           Format de sortie (markdown, json, text)
              --output           Chemin du fichier de sortie
              --max-files        Nombre maximal de fichiers à inclure
              --show-metadata    Afficher les métadonnées (oui/non)
              --show-content     Afficher le contenu des fichiers (oui/non)
              --audit            Afficher un rapport détaillé
              --dry-run          Simuler l'extraction sans écrire de fichier
              --log-level        Niveau de log (debug, info, warning, error)
              --export-decisions Exporter les décisions de classification (JSON)
              --debug-log        Chemin du fichier de log debug (optionnel)
              --no-progress      Désactive la barre de progression
            """.format(model=_model_name)
            import logging
            logger = None
            if debug_log:
                log_path = Path(debug_log)
                if not log_path.is_absolute():
                    log_path = Path(source).resolve() / debug_log
                logger = logging.getLogger()
                logger.setLevel(logging.DEBUG)
                file_handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
                formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
                logger.info(f"[DEBUG] Log activé dans {log_path}")
            model_config = MODEL_CONFIGS[_model_name]
            root_path = Path(source).resolve()
            if not root_path.exists() or not root_path.is_dir():
                click.echo(f"Chemin source invalide : {root_path}", err=True)
                sys.exit(1)
            start_total = time.time()
            click.echo(f"[DEBUG] Début scan de l'arborescence pour {root_path}")
            start_scan = time.time()
            root_node = build_filesystem_tree(root_path)
            click.echo(f"[DEBUG] Fin scan arborescence en {time.time() - start_scan:.2f}s")
            # Extraction prioritaire des fichiers Python, tests, YAML de config LLM/règles
            import glob
            import os
            extra_files = []
            for pattern in [
                str(root_path / "src/gitingest/**/*.py"),
                str(root_path / "tests/**/*.py"),
                str(root_path / "src/gitingest/**/*.yaml"),
                str(root_path / "src/gitingest/**/*.yml"),
                str(root_path / "src/gitingest/**/*.json"),
            ]:
                extra_files.extend(glob.glob(pattern, recursive=True))
            extra_files = list(set(extra_files))
            click.echo(f"[DEBUG] {len(extra_files)} fichiers extra trouvés")
            start_extract = time.time()
            click.echo(f"[DEBUG] Début extract_repo_context...")
            repo_context = extract_repo_context(
                root_node,
                model_config,
                repo_name=root_path.name,
            )
            click.echo(f"[DEBUG] Fin extract_repo_context en {time.time() - start_extract:.2f}s")
            existing_paths = {f.path for f in repo_context.files}
            from gitingest.schemas.schemas import FileNode, FileType, FileImportance
            added = 0
            for fpath in extra_files:
                rel_path = os.path.relpath(fpath, root_path)
                if rel_path not in existing_paths:
                    try:
                        with open(fpath, "r", encoding="utf-8") as f:
                            content = f.read()
                    except Exception:
                        content = ""
                    node = FileNode(
                        path=rel_path,
                        file_type=FileType.SOURCE,
                        importance=FileImportance.HIGH,
                        size=os.path.getsize(fpath),
                        language="python" if fpath.endswith(".py") else None,
                        extra={"content": content}
                    )
                    repo_context.files.append(node)
                    added += 1
            click.echo(f"[DEBUG] {added} fichiers extra ajoutés à repo_context.files")
            click.echo(f"[DEBUG] Nombre total de fichiers à traiter : {len(repo_context.files)}")
            click.echo(f"[DEBUG] Temps total de préparation : {time.time() - start_total:.2f}s")
            # Options de formatage IA : on force show_content=True sauf si --no-content
            markdown_options = {"max_files": max_files, "show_metadata": show_metadata, "show_content": show_content}
            # Génération d'un résumé et d'un tree minimal (compatible RepoContext)
            summary = f"# Dépôt : {getattr(repo_context, 'repo_name', root_path.name)}"
            if getattr(repo_context, 'branch', None):
                summary += f"\n**Branche** : `{repo_context.branch}`"
            if getattr(repo_context, 'commit', None):
                summary += f"\n**Commit** : `{repo_context.commit}`"
            summary += f"\n\n## Fichiers extraits ({len(repo_context.files)})\n"
            # Arborescence simple (liste des chemins)
            tree = "\n".join(f"- {f.path}" for f in repo_context.files)
            content = ""
            formatted = summary + "\n" + tree + "\n" + content
            # Audit option
            if audit:
                click.echo("\n[Audit] Décisions de classification et d'extraction :")
                if logger:
                    logger.info(f"[DEBUG] Nombre de fichiers dans repo_context.files : {len(repo_context.files)}")
                for file in repo_context.files:
                    if logger:
                        logger.info(f"[DEBUG] Traitement fichier : {getattr(file, 'path', None)} | taille : {getattr(file, 'size', None)} | type : {getattr(file, 'file_type', None)}")
                    click.echo(f"- {file.path} | Type: {file.file_type.name} | Importance: {file.importance.name} | Tronqué: {file.extra.get('truncated', False)}")
            # Export des décisions
            if export_decisions:
                import json
                with open(export_decisions, "w", encoding="utf-8") as f:
                    json.dump([
                        {
                            "path": file.path,
                            "file_type": file.file_type.name,
                            "importance": file.importance.name,
                            "truncated": file.extra.get("truncated", False),
                        } for file in repo_context.files
                    ], f, ensure_ascii=False, indent=2)
                click.echo(f"Décisions exportées dans : {export_decisions}")
            # Gestion de l'output :
            # 1. Si --dry-run, on affiche dans le terminal et on n'écrit rien
            if dry_run:
                click.echo("[Dry-run] Aucun fichier n'a été écrit.")
                click.echo(formatted)
                return
            # 2. Si --output explicite, on écrit dans ce fichier
            if output:
                # Remplacer le fichier s'il existe déjà
                if os.path.exists(output):
                    os.remove(output)
                with open(output, "w", encoding="utf-8") as f:
                    f.write(formatted)
                click.echo(f"Contexte optimisé écrit dans : {output}")
                return
            # 3. Sinon, on applique le comportement optimisé IA :
            #    - on écrit dans un fichier .txt compact, format JSONL (une entrée JSON par ligne)
            #    - chaque fichier ou section du contexte est sérialisé en JSON compact, sans markdown ni décor
            #    - on affiche le chemin du fichier créé
            import json, os
            max_size = model_config.max_file_size
            part = 1
            current_lines = []
            current_size = 0
            output_files = []
            # Correction : base_dir = répertoire courant (là où la commande est lancée)
            base_dir = Path(os.getcwd())
            def write_part(lines, truncated=False):
                nonlocal part, output_files
                fname = base_dir / f"{root_path.name}_{_model_name}_part{part}.txt"
                # Remplacer le fichier s'il existe déjà
                if fname.exists():
                    fname.unlink()
                with open(fname, "w", encoding="utf-8") as f:
                    for l in lines:
                        f.write(l + "\n")
                    if truncated:
                        f.write(json.dumps({"truncated": True}, ensure_ascii=False) + "\n")
                size = fname.stat().st_size
                if logger:
                    logger.info(f"[DEBUG] Output écrit : {fname} ({size} octets)")
                output_files.append(str(fname))
                part += 1
            # On commence par écrire le résumé et le tree en premier(s) fichier(s), en respectant la taille max
            meta_lines = [json.dumps({"summary": summary}, ensure_ascii=False), json.dumps({"tree": tree}, ensure_ascii=False)]
            current_meta_lines = []
            current_meta_size = 0
            for l in meta_lines:
                l_size = len((l + "\n").encode("utf-8"))
                if current_meta_size + l_size > max_size:
                    if current_meta_lines:
                        write_part(current_meta_lines, truncated=False)
                        current_meta_lines = []
                        current_meta_size = 0
                current_meta_lines.append(l)
                current_meta_size += l_size
            if current_meta_lines:
                write_part(current_meta_lines, truncated=False)
            # Puis on écrit le contenu des fichiers (Python, tests, YAML, etc.)
            click.echo("[Étape] Scan de l'arborescence...")
            files_to_iterate = repo_context.files
            use_progress = (not no_progress) and len(files_to_iterate) > 10
            file_iter = tqdm(files_to_iterate, desc="Traitement des fichiers", unit="fichier", disable=not use_progress)
            for file in file_iter:
                try:
                    tqdm.write(f"[DEBUG] Début traitement : {file.path}")
                    obj = {
                        "path": file.path,
                        "type": file.file_type.name,
                        "importance": file.importance.name,
                        "content": file.extra.get("content", ""),
                        "truncated": file.extra.get("truncated", False)
                    }
                    content = obj["content"]
                    base_obj = {k: v for k, v in obj.items() if k != "content"}
                    base_line = json.dumps({**base_obj, "content": ""}, ensure_ascii=False, separators=(",", ":"))
                    base_size = len((base_line + "\n").encode("utf-8"))
                    content_bytes = content.encode("utf-8")
                    offset = 0
                    while offset < len(content_bytes):
                        tqdm.write(f"[DEBUG] Découpage {file.path} offset={offset} / {len(content_bytes)}")
                        max_content_size = max_size - base_size
                        chunk = content_bytes[offset:offset+max_content_size]
                        chunk_str = chunk.decode("utf-8", errors="ignore")
                        is_truncated = offset + max_content_size < len(content_bytes)
                        obj["content"] = chunk_str
                        obj["truncated"] = is_truncated
                        line = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
                        line_size = len((line + "\n").encode("utf-8"))
                        if line_size > max_size:
                            sub_chunk_size = max_content_size
                            found = False
                            while sub_chunk_size > 0:
                                sub_chunk = content_bytes[offset:offset+sub_chunk_size]
                                sub_chunk_str = sub_chunk.decode("utf-8", errors="ignore")
                                obj["content"] = sub_chunk_str
                                obj["truncated"] = True
                                sub_line = json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
                                sub_line_size = len((sub_line + "\n").encode("utf-8"))
                                if sub_line_size <= max_size:
                                    if current_size + sub_line_size > max_size and current_lines:
                                        write_part(current_lines, truncated=True)
                                        current_lines = []
                                        current_size = 0
                                    current_lines.append(sub_line)
                                    current_size += sub_line_size
                                    offset += sub_chunk_size
                                    found = True
                                    break
                                sub_chunk_size -= 1
                            if not found:
                                tqdm.write(f"[DEBUG] Chunk impossible à découper pour {file.path} à l'offset {offset}, on saute 1000 octets")
                                offset += 1000
                                continue
                        if current_size + line_size > max_size:
                            if current_lines:
                                write_part(current_lines, truncated=False)
                                current_lines = []
                                current_size = 0
                            current_lines.append(line)
                            current_size = line_size
                        else:
                            current_lines.append(line)
                            current_size += line_size
                        if current_size >= max_size:
                            write_part(current_lines, truncated=is_truncated)
                            current_lines = []
                            current_size = 0
                        offset += max_content_size
                    tqdm.write(f"[DEBUG] Fin traitement : {file.path}")
                except Exception as e:
                    tqdm.write(f"[ERREUR] Impossible de traiter {file.path}: {e}")
            click.echo("[Étape] Découpage et écriture des outputs...")
            if use_progress:
                file_iter.close()
            click.echo(f"Contexte optimisé (format IA) écrit dans : {', '.join(output_files)}")
        return model_command

    for model_name in MODEL_CONFIGS.keys():
        ai.add_command(make_model_command(model_name))

    @cli.command()
    @click.argument("source", type=str, default=".")
    @click.option("--output", "-o", default=None, help="Chemin du fichier de sortie (par défaut: <repo_name>.txt dans le dossier courant)")
    @click.option("--max-size", "-s", default=MAX_FILE_SIZE, help="Taille maximale d'un fichier à traiter (en octets)")
    @click.option("--exclude-pattern", "-e", multiple=True, help="Patterns à exclure (ex: *.md, tests/*)")
    @click.option("--include-pattern", "-i", multiple=True, help="Patterns à inclure (ex: *.py, src/*)")
    @click.option("--branch", "-b", default=None, help="Branche à cloner et analyser")
    def main(
        source: str,
        output: str,
        max_size: int,
        exclude_pattern,
        include_pattern,
        branch,
    ):
        """
        Point d'entrée principal de la CLI (analyse classique).

        SOURCE : chemin du dépôt à analyser (par défaut: .)

        Exemples d'utilisation :
          gitingest ./mon-projet --max-size 100000 --exclude-pattern '*.md' --output resultat.txt
          gitingest ./src --include-pattern '*.py' --branch main

        Options principales :
          --output           Chemin du fichier de sortie
          --max-size         Taille maximale d'un fichier à traiter (en octets)
          --exclude-pattern  Patterns à exclure (ex: *.md, tests/*)
          --include-pattern  Patterns à inclure (ex: *.py, src/*)
          --branch           Branche à cloner et analyser
        """
        asyncio.run(_async_main(source, output, max_size, exclude_pattern, include_pattern, branch))

    async def _async_main(
        source: str,
        output: str,
        max_size: int,
        exclude_pattern,
        include_pattern,
        branch,
    ) -> None:
        try:
            from gitingest.config import OUTPUT_FILE_NAME
            exclude_patterns = set(exclude_pattern)
            include_patterns = set(include_pattern)
            if not output:
                output = OUTPUT_FILE_NAME
            summary, _, _ = await ingest_async(source, max_size, include_patterns, exclude_patterns, branch, output=output)
            click.echo(f"Analysis complete! Output written to: {output}")
            click.echo("\nSummary:")
            click.echo(summary)
        except Exception as exc:
            click.echo(f"Error: {exc}", err=True)
            raise click.Abort()

    return cli

cli = create_cli()

if __name__ == "__main__":
    cli()

main = cli
