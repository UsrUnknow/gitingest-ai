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
import os
import json
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

def create_cli():
    @click.group()
    def cli():
        """Gitingest CLI (analyse classique et optimisation LLM)"""
        pass

    @cli.group()
    def ai():
        """Extraction optimisée pour LLM (GPT, Claude, Gemini, etc.)"""
        pass

    @ai.command()
    @click.argument("directories", nargs=-1, required=True)
    @click.option("--model", "-m", default="gpt-4", help="Modèle LLM à utiliser pour l'optimisation")
    @click.option("--output-dir", "-o", default=".", help="Répertoire de sortie pour les fichiers digest")
    @click.option("--include-ext", "-i", multiple=True, help="Extensions à inclure (ex: .py, .js)")
    @click.option("--exclude-ext", "-e", multiple=True, help="Extensions à exclure (ex: .log, .tmp)")
    @click.option("--exclude-dirs", "-d", multiple=True, help="Répertoires à exclure (ex: node_modules, .git)")
    @click.option("--exclude-files", "-f", multiple=True, help="Fichiers à exclure (ex: *.log, temp*)")
    @click.option("--max-files", default=None, type=int, help="Nombre maximal de fichiers par projet")
    @click.option("--dry-run", is_flag=True, help="Simuler l'extraction sans écrire de fichiers")
    @click.option("--verbose", "-v", is_flag=True, help="Affichage détaillé")
    @click.option("--parallel", "-p", default=4, type=int, help="Nombre de projets à traiter en parallèle")
    def batch(directories, model, output_dir, include_ext, exclude_ext, exclude_dirs, exclude_files, max_files, dry_run, verbose, parallel):
        """
        Traite plusieurs répertoires en parallèle et génère un fichier digest par projet.
        
        Le nom du fichier de sortie sera automatiquement généré à partir du nom du répertoire.
        
        Exemples d'utilisation :
          gitingest ai batch ./projet1 ./projet2 ./projet3 --model gpt-4o
          gitingest ai batch ./src/* --exclude-dirs node_modules .git --exclude-ext .log .tmp
          gitingest ai batch ./projects/* --include-ext .py .js .ts --output-dir ./digests
        """
        
        # Configuration par défaut pour l'exclusion
        default_exclude_dirs = {
            "node_modules", ".git", "__pycache__", ".pytest_cache", ".mypy_cache", 
            "venv", ".venv", "env", ".env", "dist", "build", ".next", ".nuxt",
            "coverage", ".coverage", "htmlcov", ".tox", ".cache", "target",
            "vendor", "deps", "_build", ".elixir_ls"
        }
        
        default_exclude_files = {
            "*.log", "*.tmp", "*.temp", "*.bak", "*.swp", "*.swo", "*.DS_Store",
            "*.pyc", "*.pyo", "*.pyd", "*.class", "*.o", "*.so", "*.dll",
            "package-lock.json", "yarn.lock", "composer.lock", "Gemfile.lock"
        }
        
        # Fusionner avec les exclusions utilisateur
        exclude_dirs_set = default_exclude_dirs.union(set(exclude_dirs))
        exclude_files_set = default_exclude_files.union(set(exclude_files))
        
        if model not in MODEL_CONFIGS:
            click.echo(f"Modèle LLM non supporté : {model}. Modèles disponibles : {', '.join(MODEL_CONFIGS.keys())}", err=True)
            sys.exit(1)
        
        model_config = MODEL_CONFIGS[model]
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Résoudre les répertoires (gestion des wildcards)
        resolved_dirs = []
        for directory in directories:
            if "*" in directory or "?" in directory:
                # Gestion des wildcards
                resolved_dirs.extend(glob.glob(directory))
            else:
                resolved_dirs.append(directory)
        
        # Filtrer les répertoires valides
        valid_dirs = []
        for dir_path in resolved_dirs:
            path = Path(dir_path).resolve()
            if path.exists() and path.is_dir():
                valid_dirs.append(path)
            elif verbose:
                click.echo(f"Ignoré (n'existe pas ou n'est pas un répertoire) : {dir_path}")
        
        if not valid_dirs:
            click.echo("Aucun répertoire valide trouvé.", err=True)
            sys.exit(1)
        
        click.echo(f"Traitement de {len(valid_dirs)} répertoire(s) avec le modèle {model}")
        if verbose:
            click.echo(f"Répertoires exclus : {', '.join(sorted(exclude_dirs_set))}")
            click.echo(f"Fichiers exclus : {', '.join(sorted(exclude_files_set))}")
        
        def process_directory(directory):
            """Traite un répertoire et retourne les résultats"""
            try:
                project_name = directory.name
                output_file = output_path / f"{project_name}.jsonl"
                
                if verbose:
                    click.echo(f"Traitement de {directory} -> {output_file}")
                
                # Construire l'arbre du système de fichiers avec filtrage
                root_node = build_filesystem_tree(directory)
                
                # Filtrer les fichiers selon les critères
                filtered_node = _filter_filesystem_tree(
                    root_node, 
                    include_ext, 
                    exclude_ext, 
                    exclude_dirs_set, 
                    exclude_files_set
                )
                
                # Extraire le contexte
                repo_context = extract_repo_context(
                    filtered_node,
                    model_config,
                    repo_name=project_name,
                )
                
                # Limiter le nombre de fichiers si spécifié
                if max_files and len(repo_context.files) > max_files:
                    repo_context.files = repo_context.files[:max_files]
                
                # Lire le contenu des fichiers
                for file_node in repo_context.files:
                    file_path = directory / file_node.path
                    if file_path.exists() and file_path.is_file():
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                                if len(content.encode('utf-8')) > model_config.max_file_size:
                                    # Tronquer si trop grand
                                    content = content[:model_config.max_file_size//2] + "\n... [CONTENU TRONQUÉ] ..."
                                    file_node.extra['truncated'] = True
                                file_node.extra['content'] = content
                        except (UnicodeDecodeError, IOError):
                            file_node.extra['content'] = "[FICHIER BINAIRE OU ILLISIBLE]"
                
                if not dry_run:
                    # Écrire au format JSONL
                    with open(output_file, 'w', encoding='utf-8') as f:
                        # Métadonnées du projet
                        metadata = {
                            "type": "metadata",
                            "project_name": project_name,
                            "total_files": len(repo_context.files),
                            "model": model,
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                        }
                        f.write(json.dumps(metadata, ensure_ascii=False) + '\n')
                        
                        # Fichiers
                        for file_node in repo_context.files:
                            file_data = {
                                "type": "file",
                                "path": file_node.path,
                                "file_type": file_node.file_type.name,
                                "importance": file_node.importance.name,
                                "size": file_node.size,
                                "language": file_node.language,
                                "content": file_node.extra.get('content', ''),
                                "truncated": file_node.extra.get('truncated', False)
                            }
                            f.write(json.dumps(file_data, ensure_ascii=False) + '\n')
                
                return {
                    'project': project_name,
                    'output_file': str(output_file),
                    'files_count': len(repo_context.files),
                    'success': True,
                    'error': None
                }
                
            except Exception as e:
                return {
                    'project': directory.name,
                    'output_file': None,
                    'files_count': 0,
                    'success': False,
                    'error': str(e)
                }
        
        # Traitement en parallèle
        results = []
        with ThreadPoolExecutor(max_workers=parallel) as executor:
            if verbose:
                # Avec barre de progression
                futures = {executor.submit(process_directory, dir_path): dir_path for dir_path in valid_dirs}
                with tqdm(total=len(valid_dirs), desc="Traitement des projets") as pbar:
                    for future in as_completed(futures):
                        result = future.result()
                        results.append(result)
                        pbar.update(1)
                        if result['success']:
                            pbar.set_postfix({"Dernière réussite": result['project']})
            else:
                # Sans barre de progression
                futures = [executor.submit(process_directory, dir_path) for dir_path in valid_dirs]
                for future in as_completed(futures):
                    results.append(future.result())
        
        # Afficher les résultats
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        click.echo(f"\n=== RÉSULTATS ===")
        click.echo(f"Projets traités avec succès : {len(successful)}")
        click.echo(f"Projets échoués : {len(failed)}")
        
        if successful:
            click.echo("\n=== FICHIERS GÉNÉRÉS ===")
            for result in successful:
                click.echo(f"  {result['project']}: {result['output_file']} ({result['files_count']} fichiers)")
        
        if failed:
            click.echo("\n=== ERREURS ===")
            for result in failed:
                click.echo(f"  {result['project']}: {result['error']}")
        
        if not dry_run:
            click.echo(f"\nFichiers digest créés dans : {output_path}")
        else:
            click.echo(f"\n[DRY RUN] Aucun fichier n'a été créé.")

    def _filter_filesystem_tree(node, include_ext, exclude_ext, exclude_dirs, exclude_files):
        """Filtre récursivement l'arbre du système de fichiers"""
        if node.type == FileSystemNodeType.DIRECTORY:
            # Vérifier si le répertoire doit être exclu
            if node.path.name in exclude_dirs:
                return None
            
            # Filtrer les enfants récursivement
            filtered_children = []
            for child in node.children:
                filtered_child = _filter_filesystem_tree(child, include_ext, exclude_ext, exclude_dirs, exclude_files)
                if filtered_child is not None:
                    filtered_children.append(filtered_child)
            
            # Retourner le nœud avec les enfants filtrés
            if filtered_children:
                node.children = filtered_children
                return node
            return None
            
        elif node.type == FileSystemNodeType.FILE:
            filename = node.path.name
            extension = node.path.suffix
            
            # Vérifier les patterns d'exclusion de fichiers
            for pattern in exclude_files:
                import fnmatch
                if fnmatch.fnmatch(filename, pattern):
                    return None
            
            # Vérifier les extensions
            if include_ext:
                if extension not in include_ext:
                    return None
            
            if exclude_ext:
                if extension in exclude_ext:
                    return None
            
            return node
        
        return node

    def make_model_command(model_name):
        @ai.command(name=model_name)
        @click.argument("source", type=str, default=".")
        @click.option("--format", "-f", default="markdown", show_default=True, type=click.Choice(["markdown", "json", "text"]), help="Format de sortie du contexte optimisé.")
        @click.option("--output", "-o", default=None, help="Chemin du fichier de sortie (par défaut: <nom_du_repertoire>.jsonl)")
        @click.option("--max-files", default=None, type=int, help="Nombre maximal de fichiers à inclure dans le contexte.")
        @click.option("--show-metadata/--no-metadata", default=True, help="Afficher les métadonnées des fichiers dans le format Markdown.")
        @click.option("--show-content/--no-content", default=True, help="Afficher le contenu des fichiers dans le format Markdown.")
        @click.option("--audit", is_flag=True, help="Afficher un rapport détaillé des décisions de classification et d'extraction.")
        @click.option("--dry-run", is_flag=True, help="Simuler l'extraction sans écrire de fichier.")
        @click.option("--log-level", default="info", type=click.Choice(["debug", "info", "warning", "error"]), help="Niveau de log à utiliser.")
        @click.option("--export-decisions", default=None, help="Chemin d'export des décisions de classification (JSON).")
        @click.option("--debug-log", default=None, help="Chemin du fichier de log debug (optionnel)")
        @click.option('--no-progress', is_flag=True, default=False, help='Désactive la barre de progression.')
        @click.option("--include-ext", "-i", multiple=True, help="Extensions à inclure (ex: .py, .js)")
        @click.option("--exclude-ext", "-e", multiple=True, help="Extensions à exclure (ex: .log, .tmp)")
        @click.option("--exclude-dirs", "-d", multiple=True, help="Répertoires à exclure (ex: node_modules, .git)")
        @click.option("--exclude-files", "-f", multiple=True, help="Fichiers à exclure (ex: *.log, temp*)")
        def model_command(source, format, output, max_files, show_metadata, show_content, audit, dry_run, log_level, export_decisions, debug_log, no_progress, include_ext, exclude_ext, exclude_dirs, exclude_files, _model_name=model_name):
            """
            Extraction optimisée pour le modèle LLM preset : {model}

            SOURCE : chemin du dossier racine du dépôt à analyser (par défaut: .)

            Exemples d'utilisation :
              gitingest ai {model} ./mon-projet --dry-run
              gitingest ai {model} ./src --format json --output contexte.json
              gitingest ai {model} ./projet --include-ext .py .js --exclude-dirs node_modules

            Options principales :
              --format           Format de sortie (markdown, json, text)
              --output           Chemin du fichier de sortie (par défaut: <nom_du_repertoire>.jsonl)
              --max-files        Nombre maximal de fichiers à inclure
              --show-metadata    Afficher les métadonnées (oui/non)
              --show-content     Afficher le contenu des fichiers (oui/non)
              --audit            Afficher un rapport détaillé
              --dry-run          Simuler l'extraction sans écrire de fichier
              --log-level        Niveau de log (debug, info, warning, error)
              --export-decisions Exporter les décisions de classification (JSON)
              --debug-log        Chemin du fichier de log debug (optionnel)
              --no-progress      Désactive la barre de progression
              --include-ext      Extensions à inclure
              --exclude-ext      Extensions à exclure
              --exclude-dirs     Répertoires à exclure
              --exclude-files    Fichiers à exclure
            """.format(model=_model_name)
            
            # Configuration par défaut pour l'exclusion
            default_exclude_dirs = {
                "node_modules", ".git", "__pycache__", ".pytest_cache", ".mypy_cache", 
                "venv", ".venv", "env", ".env", "dist", "build", ".next", ".nuxt",
                "coverage", ".coverage", "htmlcov", ".tox", ".cache", "target",
                "vendor", "deps", "_build", ".elixir_ls"
            }
            
            default_exclude_files = {
                "*.log", "*.tmp", "*.temp", "*.bak", "*.swp", "*.swo", "*.DS_Store",
                "*.pyc", "*.pyo", "*.pyd", "*.class", "*.o", "*.so", "*.dll",
                "package-lock.json", "yarn.lock", "composer.lock", "Gemfile.lock"
            }
            
            # Fusionner avec les exclusions utilisateur
            exclude_dirs_set = default_exclude_dirs.union(set(exclude_dirs))
            exclude_files_set = default_exclude_files.union(set(exclude_files))
            
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
            
            # Appliquer les filtres
            filtered_node = _filter_filesystem_tree(
                root_node, 
                include_ext, 
                exclude_ext, 
                exclude_dirs_set, 
                exclude_files_set
            )
            
            click.echo(f"[DEBUG] Fin scan arborescence en {time.time() - start_scan:.2f}s")
            
            start_extract = time.time()
            click.echo(f"[DEBUG] Début extract_repo_context...")
            repo_context = extract_repo_context(
                filtered_node,
                model_config,
                repo_name=root_path.name,
            )
            click.echo(f"[DEBUG] Fin extract_repo_context en {time.time() - start_extract:.2f}s")
            
            # Lire le contenu des fichiers
            for file_node in repo_context.files:
                file_path = root_path / file_node.path
                if file_path.exists() and file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            # Tronquer si nécessaire
                            if len(content.encode('utf-8')) > model_config.max_file_size:
                                content = content[:model_config.max_file_size//2] + "\n... [CONTENU TRONQUÉ] ..."
                                file_node.extra['truncated'] = True
                            file_node.extra['content'] = content
                    except (UnicodeDecodeError, IOError):
                        file_node.extra['content'] = "[FICHIER BINAIRE OU ILLISIBLE]"
            
            click.echo(f"[DEBUG] Nombre total de fichiers à traiter : {len(repo_context.files)}")
            click.echo(f"[DEBUG] Temps total de préparation : {time.time() - start_total:.2f}s")
            
            # Génération du nom de fichier de sortie automatique
            if not output:
                output = f"{root_path.name}.jsonl"
            
            # Gestion du dry-run
            if dry_run:
                click.echo("[Dry-run] Aucun fichier n'a été écrit.")
                click.echo(f"Projet : {root_path.name}")
                click.echo(f"Nombre de fichiers : {len(repo_context.files)}")
                click.echo(f"Fichier de sortie : {output}")
                if repo_context.files:
                    click.echo("Fichiers inclus :")
                    for file_node in repo_context.files[:10]:  # Afficher les 10 premiers
                        click.echo(f"  - {file_node.path} ({file_node.file_type.name})")
                    if len(repo_context.files) > 10:
                        click.echo(f"  ... et {len(repo_context.files) - 10} autres fichiers")
                
                # Audit option (même en dry-run)
                if audit:
                    click.echo("\n[Audit] Décisions de classification et d'extraction :")
                    for file in repo_context.files:
                        click.echo(f"- {file.path} | Type: {file.file_type.name} | Importance: {file.importance.name} | Tronqué: {file.extra.get('truncated', False)}")
                
                # Export des décisions (même en dry-run)
                if export_decisions:
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
                
                return
            
            # Écriture du fichier de sortie
            with open(output, 'w', encoding='utf-8') as f:
                # Métadonnées du projet
                metadata = {
                    "type": "metadata",
                    "project_name": root_path.name,
                    "total_files": len(repo_context.files),
                    "model": _model_name,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
                f.write(json.dumps(metadata, ensure_ascii=False) + '\n')
                
                # Fichiers
                for file_node in repo_context.files:
                    file_data = {
                        "type": "file",
                        "path": file_node.path,
                        "file_type": file_node.file_type.name,
                        "importance": file_node.importance.name,
                        "size": file_node.size,
                        "language": file_node.language,
                        "content": file_node.extra.get('content', ''),
                        "truncated": file_node.extra.get('truncated', False)
                    }
                    f.write(json.dumps(file_data, ensure_ascii=False) + '\n')
            
            click.echo(f"Contexte optimisé écrit dans : {output}")
            
            # Audit option
            if audit:
                click.echo("\n[Audit] Décisions de classification et d'extraction :")
                for file in repo_context.files:
                    click.echo(f"- {file.path} | Type: {file.file_type.name} | Importance: {file.importance.name} | Tronqué: {file.extra.get('truncated', False)}")
            
            # Export des décisions
            if export_decisions:
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
        
        return model_command

    for model_name in MODEL_CONFIGS.keys():
        ai.add_command(make_model_command(model_name))

    @cli.command()
    @click.argument("source", type=str, default=".")
    @click.option("--output", "-o", default=None, help="Chemin du fichier de sortie (par défaut: stdout)")
    @click.option("--lines", "-n", default=40, show_default=True, help="Nombre de lignes à extraire par fichier clé.")
    def extract_key_files(source, output, lines):
        """
        Extrait les fichiers clés d'un projet (README, contrôleur, entité, repository, test, etc.)
        et affiche un rapport structuré (JSON) universel, quel que soit le langage (Python, JS, C#, Java, etc.).

        Exemples :
          gitingest extract-key-files ./mon-projet
          gitingest extract-key-files . --output rapport.json --lines 50
        """
        from pathlib import Path
        import json
        from gitingest.utils.key_file_detection import find_key_files, generate_extraction_report
        root_path = Path(source).resolve()
        if not root_path.exists() or not root_path.is_dir():
            click.echo(f"Chemin source invalide : {root_path}", err=True)
            return
        key_files = find_key_files(root_path)
        report = generate_extraction_report(key_files, n_lines=lines)
        if output:
            with open(output, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            click.echo(f"Rapport d'extraction écrit dans : {output}")
        else:
            click.echo(json.dumps(report, ensure_ascii=False, indent=2))

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
