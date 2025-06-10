# Traitement en Lot avec Gitingest

Cette documentation explique comment utiliser les nouvelles fonctionnalités de traitement en lot de Gitingest pour analyser facilement plusieurs projets à la fois.

## Vue d'ensemble

Les nouvelles fonctionnalités permettent de :
- ✅ Traiter plusieurs répertoires en parallèle
- ✅ Générer automatiquement un fichier digest par projet
- ✅ Filtrer intelligemment les fichiers selon leur importance pour l'IA
- ✅ Exclure automatiquement les fichiers inutiles
- ✅ Personnaliser les filtres selon vos besoins
- ✅ Utiliser des presets optimisés pour différents modèles LLM

## Commande `batch`

### Utilisation de base

```bash
# Traiter plusieurs projets
gitingest ai batch ./projet1 ./projet2 ./projet3

# Avec wildcards
gitingest ai batch ./projects/*

# Modèle spécifique
gitingest ai batch ./src/* --model claude-3-sonnet
```

### Options disponibles

| Option | Description | Exemple |
|--------|-------------|---------|
| `--model, -m` | Modèle LLM à utiliser | `--model gpt-4o` |
| `--output-dir, -o` | Répertoire de sortie | `--output-dir ./digests` |
| `--include-ext, -i` | Extensions à inclure | `--include-ext .py .js` |
| `--exclude-ext, -e` | Extensions à exclure | `--exclude-ext .log .tmp` |
| `--exclude-dirs, -d` | Répertoires à exclure | `--exclude-dirs cache logs` |
| `--exclude-files, -f` | Fichiers à exclure | `--exclude-files "*.min.js" "temp*"` |
| `--max-files` | Limite de fichiers par projet | `--max-files 100` |
| `--parallel, -p` | Projets en parallèle | `--parallel 8` |
| `--verbose, -v` | Mode détaillé | `--verbose` |
| `--dry-run` | Simulation sans écriture | `--dry-run` |

### Exemples pratiques

```bash
# Projets Python uniquement
gitingest ai batch ./my-projects/* --include-ext .py --model gpt-4

# Projets web avec exclusions personnalisées
gitingest ai batch ./web-apps/* \
  --include-ext .js .ts .jsx .tsx .html .css \
  --exclude-dirs node_modules dist build \
  --model claude-3-sonnet

# Traitement rapide avec simulation
gitingest ai batch ./test-projects/* --dry-run --verbose

# Traitement intensif
gitingest ai batch ./large-projects/* \
  --parallel 8 \
  --max-files 200 \
  --output-dir ./results
```

## Filtrage Intelligent

### Exclusions par défaut

Le système exclut automatiquement :

**Répertoires :**
- `node_modules`, `venv`, `.git`, `__pycache__`
- `dist`, `build`, `target`, `.cache`
- `.vscode`, `.idea`, `.pytest_cache`

**Fichiers :**
- `*.log`, `*.tmp`, `*.pyc`, `*.class`
- `package-lock.json`, `yarn.lock`
- `*.min.js`, `*.min.css`

**Extensions importantes incluses :**
- Code source : `.py`, `.js`, `.ts`, `.java`, `.go`, `.rs`, etc.
- Configuration : `.json`, `.yaml`, `.toml`, `.env`
- Documentation : `.md`, `.rst`, `.txt`

### Personnalisation des filtres

```bash
# Inclure seulement certaines extensions
gitingest ai batch ./projects/* --include-ext .py .yaml .json

# Exclure des extensions supplémentaires
gitingest ai batch ./projects/* --exclude-ext .log .backup .old

# Exclure des répertoires spécifiques
gitingest ai batch ./projects/* --exclude-dirs temp cache logs

# Exclure des patterns de fichiers
gitingest ai batch ./projects/* --exclude-files "*.min.*" "backup*" "temp*"
```

## Format de Sortie

Les fichiers générés utilisent le format JSONL (JSON Lines) optimisé pour l'IA :

```jsonl
{"type": "metadata", "project_name": "mon-projet", "total_files": 42, "model": "gpt-4o", "timestamp": "2024-01-15 14:30:00"}
{"type": "file", "path": "src/main.py", "file_type": "SOURCE", "importance": "HIGH", "size": 1024, "language": "python", "content": "# Code source...", "truncated": false}
{"type": "file", "path": "README.md", "file_type": "DOCUMENTATION", "importance": "MEDIUM", "size": 512, "language": null, "content": "# Documentation...", "truncated": false}
```

### Structure du fichier

1. **Ligne 1** : Métadonnées du projet
2. **Lignes suivantes** : Un fichier par ligne avec :
   - `path` : Chemin relatif
   - `file_type` : Type (SOURCE, CONFIG, DOCUMENTATION, etc.)
   - `importance` : Importance (HIGH, MEDIUM, LOW)
   - `content` : Contenu du fichier
   - `truncated` : Indique si le contenu a été tronqué

## Script Utilitaire `quick-ingest.sh`

Un script bash simplifie l'utilisation courante :

```bash
# Installation
chmod +x scripts/quick-ingest.sh

# Utilisation
./scripts/quick-ingest.sh --help
./scripts/quick-ingest.sh ./projets/*
./scripts/quick-ingest.sh --languages py,js,ts ./web-projects/*
```

### Options du script

```bash
# Langages spécifiques (conversion automatique en extensions)
./scripts/quick-ingest.sh --languages py,js,ts ./projects/*

# Exclusions supplémentaires
./scripts/quick-ingest.sh --exclude "*.log,temp*" ./projects/*

# Modèle et parallélisme
./scripts/quick-ingest.sh --model claude-3-sonnet --parallel 8 ./projects/*
```

## Cas d'Usage Courants

### 1. Audit de Code Multi-Projets

```bash
# Analyse de tous les projets Python
gitingest ai batch ./python-projects/* \
  --include-ext .py \
  --model gpt-4o \
  --output-dir ./code-audits
```

### 2. Documentation Multi-Projets

```bash
# Focus sur documentation et configuration
gitingest ai batch ./projects/* \
  --include-ext .md .rst .txt .yaml .json .toml \
  --model claude-3-sonnet \
  --output-dir ./docs-analysis
```

### 3. Migration de Code

```bash
# Analyse pour migration (code source uniquement)
gitingest ai batch ./legacy-projects/* \
  --include-ext .js .ts .jsx .tsx \
  --exclude-dirs node_modules dist \
  --max-files 150 \
  --model gpt-4
```

### 4. Revue de Sécurité

```bash
# Focus sur fichiers critiques
gitingest ai batch ./web-apps/* \
  --include-ext .py .js .ts .php .rb \
  --exclude-files "*.test.*" "*.spec.*" \
  --model claude-3-opus \
  --output-dir ./security-review
```

## Optimisation des Performances

### Parallélisme

```bash
# Adapter selon votre machine
--parallel 4   # Par défaut
--parallel 8   # Machine puissante
--parallel 2   # Machine limitée
```

### Limitation des Fichiers

```bash
# Éviter les projets trop volumineux
--max-files 200   # Limite raisonnable
--max-files 50    # Projets très volumineux
```

### Mode Simulation

```bash
# Tester avant l'exécution réelle
gitingest ai batch ./projects/* --dry-run --verbose
```

## Intégration avec les Outils IA

### Préparation pour ChatGPT/Claude

```bash
# Format optimisé pour les LLM
gitingest ai batch ./projects/* --model gpt-4o
# Les fichiers .jsonl peuvent être directement copiés dans l'IA
```

### Traitement Post-Génération

```bash
# Convertir JSONL en texte simple si nécessaire
cat projet.jsonl | jq -r 'select(.type=="file") | "=== \(.path) ===\n\(.content)\n"'
```

## Configuration Avancée

### Fichier de Configuration

Créez `~/.gitingest/config.yaml` :

```yaml
default_model: "gpt-4o"
default_output_dir: "./ai-digests"
default_parallel: 4

exclude_patterns:
  - "*.log"
  - "*.tmp"
  - "node_modules"
  - ".git"

include_extensions:
  - ".py"
  - ".js"
  - ".ts"
  - ".md"
```

### Variables d'Environnement

```bash
export GITINGEST_MODEL="claude-3-sonnet"
export GITINGEST_OUTPUT_DIR="./digests"
export GITINGEST_PARALLEL=8
```

## Dépannage

### Problèmes Courants

1. **Mémoire insuffisante**
   ```bash
   # Réduire le parallélisme
   --parallel 2
   # Limiter les fichiers
   --max-files 100
   ```

2. **Fichiers trop volumineux**
   ```bash
   # Les gros fichiers sont automatiquement tronqués
   # Vérifiez le champ "truncated": true dans le JSON
   ```

3. **Projets ignorés**
   ```bash
   # Utiliser --verbose pour voir les détails
   --verbose --dry-run
   ```

### Logs et Debug

```bash
# Mode verbose pour détails
gitingest ai batch ./projects/* --verbose

# Mode simulation pour tester
gitingest ai batch ./projects/* --dry-run

# Vérifier les fichiers générés
ls -la ./digests/
head -n 3 ./digests/mon-projet.jsonl
```

## Bonnes Pratiques

1. **Toujours tester en mode --dry-run d'abord**
2. **Utiliser --verbose pour comprendre ce qui se passe**
3. **Adapter --parallel selon votre machine**
4. **Définir --max-files pour éviter les fichiers trop volumineux**
5. **Organiser vos fichiers de sortie dans des dossiers séparés**
6. **Utiliser les filtres pour se concentrer sur ce qui est important**
7. **Sauvegarder vos configurations dans des scripts**

Cette nouvelle approche rend gitingest beaucoup plus pratique pour l'analyse de multiples projets avec l'IA ! 🚀 