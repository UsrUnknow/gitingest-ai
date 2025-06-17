# 🔄 Guide Complet du Traitement en Lot

Le traitement en lot (batch processing) est la fonctionnalité phare de Gitingest AI, permettant de traiter plusieurs projets simultanément avec un parallélisme intelligent et une optimisation pour les LLM.

## 📋 Table des Matières

- [🎯 Vue d'ensemble](#-vue-densemble)
- [⚡ Installation et Configuration](#-installation-et-configuration)
- [🚀 Utilisation de Base](#-utilisation-de-base)
- [🔧 Options Avancées](#-options-avancées)
- [📊 Format de Sortie JSONL](#-format-de-sortie-jsonl)
- [🌐 Support Multi-Langage](#-support-multi-langage)
- [⚙️ Filtrage Intelligent](#️-filtrage-intelligent)
- [📈 Performance et Optimisation](#-performance-et-optimisation)
- [🔍 Exemples Concrets](#-exemples-concrets)
- [🛠️ Dépannage](#️-dépannage)

---

## 🎯 Vue d'ensemble

### Qu'est-ce que le traitement en lot ?

Le mode batch permet de :
- **Traiter simultanément** plusieurs répertoires/projets
- **Générer automatiquement** un fichier `.jsonl` par projet
- **Optimiser les performances** grâce au parallélisme
- **Filtrer intelligemment** selon le type de projet
- **Structurer les données** pour une consommation IA optimale

### Avantages clés

✅ **Performance** : Jusqu'à 10x plus rapide que le traitement séquentiel  
✅ **Automatisation** : Nommage et structure automatiques  
✅ **Flexibilité** : Support de tous types de projets  
✅ **Optimisation IA** : Format JSONL structuré  
✅ **Contrôle** : Parallélisme configurable  

---

## ⚡ Installation et Configuration

### Prérequis
```bash
python >= 3.8
pip install gitingest
```

### Vérification de l'installation
```bash
gitingest ai batch --help
```

### Configuration recommandée
```bash
# Variables d'environnement optionnelles
export GITINGEST_DEFAULT_PARALLEL=4
export GITINGEST_MAX_FILE_SIZE=1000000
export GITINGEST_OUTPUT_DIR="./output"
```

---

## 🚀 Utilisation de Base

### Syntaxe générale
```bash
gitingest ai batch [OPTIONS] DIRECTORIES...
```

### Exemples simples

#### Traitement de base
```bash
# Traiter 3 projets en parallèle
gitingest ai batch ./projet1 ./projet2 ./projet3
```

#### Avec parallélisme personnalisé
```bash
# 6 threads parallèles
gitingest ai batch ./src ./api ./frontend --parallel 6
```

#### Mode verbeux pour debugging
```bash
# Affichage détaillé du processus
gitingest ai batch ./projet --verbose
```

#### Simulation sans traitement
```bash
# Tester la configuration sans traitement réel
gitingest ai batch ./projet1 ./projet2 --dry-run --verbose
```

---

## 🔧 Options Avancées

### Options de parallélisation

| Option | Description | Défaut | Exemple |
|--------|-------------|--------|---------|
| `--parallel N` | Nombre de threads simultanés | 4 | `--parallel 8` |
| `--timeout N` | Timeout par projet (secondes) | 300 | `--timeout 600` |

### Options de filtrage

| Option | Description | Exemple |
|--------|-------------|---------|
| `--include-ext` | Extensions à inclure | `--include-ext .py,.js,.ts` |
| `--exclude-ext` | Extensions à exclure | `--exclude-ext .log,.tmp` |
| `--exclude-dirs` | Répertoires à ignorer | `--exclude-dirs node_modules,build` |
| `--exclude-files` | Fichiers à ignorer | `--exclude-files "*.min.js,*.bundle.*"` |
| `--max-files N` | Limite de fichiers par projet | `--max-files 500` |
| `--max-file-size N` | Taille max par fichier (bytes) | `--max-file-size 1000000` |

### Options de sortie

| Option | Description | Exemple |
|--------|-------------|---------|
| `--output-dir` | Répertoire de sortie | `--output-dir ./analysis` |
| `--format` | Format de sortie | `--format jsonl` |
| `--compress` | Compression des fichiers | `--compress gzip` |

### Exemple complet avec toutes les options
```bash
gitingest ai batch \
  ./frontend ./backend ./mobile \
  --parallel 6 \
  --include-ext .js,.jsx,.ts,.tsx,.py,.dart \
  --exclude-dirs node_modules,venv,build,.dart_tool \
  --exclude-files "*.min.js,*.bundle.*,*.pyc" \
  --max-files 1000 \
  --max-file-size 500000 \
  --output-dir ./batch-analysis \
  --timeout 600 \
  --verbose
```

---

## 📊 Format de Sortie JSONL

### Structure du fichier JSONL

Chaque projet génère un fichier `.jsonl` avec :
1. **Ligne de métadonnées** (première ligne)
2. **Une ligne par fichier** traité

### Exemple de sortie

#### Ligne de métadonnées
```json
{
  "type": "metadata",
  "project_name": "mon-projet",
  "project_path": "/path/to/mon-projet",
  "timestamp": "2024-01-15T10:30:00Z",
  "total_files": 45,
  "total_size": 234567,
  "processing_time": 2.34,
  "languages_detected": ["python", "javascript", "css"],
  "gitingest_version": "2.1.0"
}
```

#### Lignes de fichiers
```json
{
  "type": "file",
  "path": "src/main.py",
  "relative_path": "src/main.py",
  "content": "#!/usr/bin/env python3\n...",
  "size": 1234,
  "extension": ".py",
  "language": "python",
  "importance": "high",
  "is_truncated": false,
  "encoding": "utf-8"
}
```

### Traitement des fichiers volumineux

Pour les fichiers > `max_file_size` :
```json
{
  "type": "file",
  "path": "dist/bundle.js",
  "relative_path": "dist/bundle.js",
  "content": "// File truncated - original size: 2.5MB\n// First 1000 lines:\n...",
  "size": 2500000,
  "extension": ".js",
  "language": "javascript",
  "importance": "low",
  "is_truncated": true,
  "truncation_reason": "size_limit",
  "original_size": 2500000
}
```

---

## 🌐 Support Multi-Langage

### Configuration automatique par langage

Le système détecte automatiquement le type de projet et applique les filtres appropriés :

#### Python
```yaml
extensions: [.py, .pyi, .pyx, .ipynb]
exclude_dirs: [__pycache__, .pytest_cache, venv, env, build, dist, .tox]
important_files: [requirements.txt, pyproject.toml, setup.py, Pipfile]
```

#### JavaScript/Node.js
```yaml
extensions: [.js, .mjs, .cjs, .jsx]
exclude_dirs: [node_modules, .next, build, dist, coverage]
important_files: [package.json, webpack.config.js, .eslintrc.js]
```

#### TypeScript
```yaml
extensions: [.ts, .tsx, .d.ts]
exclude_dirs: [node_modules, build, dist, lib]
important_files: [tsconfig.json, package.json]
```

#### React
```yaml
extensions: [.jsx, .tsx, .js, .ts, .css, .scss, .sass]
exclude_dirs: [node_modules, .next, build, dist, coverage, .storybook-static]
important_files: [package.json, next.config.js, vite.config.js]
```

#### C#/.NET
```yaml
extensions: [.cs, .vb, .fs, .csproj, .sln]
exclude_dirs: [bin, obj, packages, TestResults, .vs]
important_files: [*.sln, *.csproj, appsettings.json, Program.cs]
```

### Détection automatique de langage

Le système utilise plusieurs heuristiques :
1. **Fichiers de configuration** (`package.json`, `requirements.txt`, etc.)
2. **Extensions dominantes** (plus de 60% des fichiers)
3. **Structure de répertoires** (`src/`, `lib/`, etc.)
4. **Fichiers spéciaux** (`.gitignore`, `Dockerfile`, etc.)

---

## ⚙️ Filtrage Intelligent

### Filtres par défaut

#### Répertoires toujours exclus
```
.git, .svn, .hg
node_modules, bower_components
__pycache__, .pytest_cache
bin, obj, build, dist
.idea, .vscode, .vs
.tmp, temp, cache
```

#### Extensions toujours exclues
```
.log, .tmp, .cache, .bak
.pyc, .pyo, .pyd
.class, .jar (sauf si Java détecté)
.exe, .dll, .so, .dylib
.min.js, .bundle.js (sauf si explicitement inclus)
```

### Filtrage personnalisé

#### Par patterns
```bash
# Exclure tous les fichiers de test
--exclude-files "*test*,*spec*"

# Inclure seulement les fichiers source
--include-ext .py,.js,.ts --exclude-dirs tests,__tests__
```

#### Par taille
```bash
# Limiter la taille des fichiers
--max-file-size 1000000  # 1MB

# Limiter le nombre de fichiers
--max-files 500
```

#### Par importance
Le système classe automatiquement les fichiers :
- **Haute** : Fichiers de configuration, README, code source principal
- **Moyenne** : Code source standard, tests
- **Basse** : Fichiers générés, assets, documentation

---

## 📈 Performance et Optimisation

### Métriques de performance

#### Benchmarks typiques
| Nombre de projets | Fichiers totaux | Temps séquentiel | Temps parallèle (4 threads) | Gain |
|-------------------|-----------------|------------------|------------------------------|------|
| 3 projets moyens | ~300 fichiers | 45s | 12s | 3.75x |
| 10 petits projets | ~500 fichiers | 60s | 8s | 7.5x |
| 5 gros projets | ~2000 fichiers | 180s | 25s | 7.2x |

### Optimisation du parallélisme

#### Calcul du nombre optimal de threads
```python
# Formule recommandée
optimal_threads = min(
    number_of_projects,
    cpu_count() * 2,
    available_memory_gb // 2
)
```

#### Exemples pratiques
```bash
# Pour 2-4 projets sur machine standard
--parallel 4

# Pour 10+ petits projets sur machine puissante
--parallel 8

# Pour projets très volumineux (>100MB chacun)
--parallel 2
```

### Gestion mémoire

#### Surveillance des ressources
```bash
# Mode verbeux pour monitoring
gitingest ai batch ./projets/* --verbose --parallel 4

# Limitation mémoire via taille de fichiers
--max-file-size 500000 --max-files 1000
```

---

## 🔍 Exemples Concrets

### Exemple 1 : Analyse Full-Stack

#### Structure du projet
```
workspace/
├── frontend/          # React + TypeScript
├── backend/           # Python FastAPI
├── mobile/            # Flutter
└── shared/            # Bibliothèques partagées
```

#### Commande
```bash
gitingest ai batch \
  ./frontend ./backend ./mobile ./shared \
  --parallel 4 \
  --include-ext .js,.jsx,.ts,.tsx,.py,.dart,.yaml \
  --exclude-dirs node_modules,venv,build,.dart_tool,coverage \
  --max-files 800 \
  --output-dir ./full-stack-analysis \
  --verbose
```

#### Résultat attendu
```
full-stack-analysis/
├── frontend.jsonl     # ~200 fichiers React/TS
├── backend.jsonl      # ~150 fichiers Python
├── mobile.jsonl       # ~300 fichiers Dart
└── shared.jsonl       # ~50 fichiers utilitaires
```

### Exemple 2 : Migration Legacy

#### Contexte
Migration d'applications .NET Framework vers .NET Core

#### Structure
```
legacy-migration/
├── old-web-app/       # ASP.NET WebForms
├── old-api/           # WCF Services
├── new-web-app/       # ASP.NET Core
└── new-api/           # Web API Core
```

#### Commande
```bash
gitingest ai batch \
  ./old-web-app ./old-api ./new-web-app ./new-api \
  --include-ext .cs,.aspx,.asmx,.config,.json \
  --exclude-dirs bin,obj,packages,TestResults \
  --exclude-files "*.designer.cs,*.resx" \
  --parallel 2 \
  --max-file-size 200000 \
  --output-dir ./migration-analysis
```

### Exemple 3 : Audit de Sécurité

#### Objectif
Analyser plusieurs microservices pour audit de sécurité

#### Commande
```bash
gitingest ai batch \
  ./auth-service ./payment-service ./user-service ./admin-service \
  --include-ext .py,.js,.ts,.yaml,.json,.env \
  --exclude-dirs venv,node_modules,__pycache__,build \
  --exclude-files "*.pyc,*.log" \
  --max-files 300 \
  --parallel 4 \
  --output-dir ./security-audit \
  --verbose
```

#### Post-traitement
```bash
# Analyse des fichiers sensibles
grep -r "password\|secret\|key\|token" ./security-audit/*.jsonl

# Recherche de vulnérabilités communes
grep -r "eval\|exec\|shell\|sql" ./security-audit/*.jsonl
```

### Exemple 4 : Documentation Automatique

#### Génération de documentation pour API

#### Commande
```bash
gitingest ai batch \
  ./api-v1 ./api-v2 ./api-v3 \
  --include-ext .py,.js,.yaml,.md \
  --exclude-dirs __pycache__,node_modules,build \
  --exclude-files "*.pyc,*.min.js" \
  --parallel 3 \
  --output-dir ./api-docs-source
```

#### Script de post-traitement
```python
#!/usr/bin/env python3
import json
import os

def extract_api_endpoints(jsonl_file):
    """Extrait les endpoints d'un fichier JSONL"""
    endpoints = []
    with open(jsonl_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data.get('type') == 'file':
                content = data.get('content', '')
                # Recherche des routes Flask/FastAPI
                if '@app.route' in content or '@router.' in content:
                    endpoints.append({
                        'file': data['path'],
                        'content': content
                    })
    return endpoints

# Traitement de tous les fichiers
for jsonl_file in os.listdir('./api-docs-source'):
    if jsonl_file.endswith('.jsonl'):
        endpoints = extract_api_endpoints(f'./api-docs-source/{jsonl_file}')
        print(f"\n=== API {jsonl_file} ===")
        for endpoint in endpoints:
            print(f"File: {endpoint['file']}")
```

---

## 🛠️ Dépannage

### Problèmes Courants

#### 1. Erreur de mémoire insuffisante
```
MemoryError: Unable to allocate array
```

**Solutions :**
```bash
# Réduire le parallélisme
--parallel 2

# Limiter la taille des fichiers
--max-file-size 500000

# Limiter le nombre de fichiers
--max-files 300
```

#### 2. Timeout sur gros projets
```
TimeoutError: Project processing exceeded 300 seconds
```

**Solutions :**
```bash
# Augmenter le timeout
--timeout 900

# Exclure plus de répertoires
--exclude-dirs node_modules,build,dist,coverage,.git

# Traiter en plusieurs fois
gitingest ai batch ./projet/src --parallel 2
gitingest ai batch ./projet/tests --parallel 2
```

#### 3. Fichiers non détectés
```
Warning: No files found matching criteria
```

**Solutions :**
```bash
# Vérifier les extensions
--include-ext .py,.js,.ts --verbose

# Vérifier les exclusions
--exclude-dirs node_modules --dry-run --verbose

# Mode debug complet
--verbose --dry-run
```

#### 4. Performance dégradée
```
Processing slower than expected
```

**Solutions :**
```bash
# Profiler le système
htop  # Vérifier CPU/mémoire

# Ajuster le parallélisme
--parallel 2  # Réduire si CPU saturé
--parallel 8  # Augmenter si CPU sous-utilisé

# Optimiser les filtres
--exclude-dirs node_modules,build,dist,coverage
--max-file-size 1000000
```

### Debugging Avancé

#### Mode debug complet
```bash
export GITINGEST_DEBUG=1
export GITINGEST_LOG_LEVEL=DEBUG

gitingest ai batch ./projet --verbose --dry-run
```

#### Logs détaillés
```bash
# Redirection vers fichier
gitingest ai batch ./projet --verbose 2> debug.log

# Analyse des logs
grep "ERROR\|WARNING" debug.log
grep "Processing" debug.log | head -10
```

#### Profiling de performance
```python
#!/usr/bin/env python3
import cProfile
import pstats
from gitingest.cli import main

# Profiling d'une commande batch
cProfile.run(
    "main(['ai', 'batch', './projet', '--parallel', '4'])",
    'profile_stats.prof'
)

# Analyse des résultats
stats = pstats.Stats('profile_stats.prof')
stats.sort_stats('cumulative').print_stats(20)
```

### Support et Communauté

#### Où obtenir de l'aide

1. **Documentation** : [docs/](../docs/)
2. **Issues GitHub** : [Issues](https://github.com/maximebausset/gitingest-ai/issues)
3. **Discussions** : [Discussions](https://github.com/maximebausset/gitingest-ai/discussions)
4. **Wiki** : [Wiki](https://github.com/maximebausset/gitingest-ai/wiki)

#### Signaler un bug

```bash
# Collecter les informations système
gitingest --version
python --version
uname -a

# Reproduire avec mode debug
gitingest ai batch ./projet --verbose --dry-run > debug.log 2>&1

# Créer une issue avec :
# - Commande exacte utilisée
# - Logs d'erreur complets
# - Structure du projet (sans code sensible)
# - Informations système
```

---

## 📚 Ressources Supplémentaires

### Documentation connexe
- [Configuration des filtres](../src/gitingest/config/default_filters.yaml)
- [Script utilitaire](../scripts/quick-ingest.sh)
- [Guide d'exemples](../exemples_usage.md)
- [Cas d'usage](../guide_cas_usage.md)

### Outils complémentaires
- **jq** : Manipulation des fichiers JSONL
- **ripgrep** : Recherche rapide dans les résultats
- **bat** : Visualisation syntax-highlighted
- **fd** : Recherche de fichiers avancée

### Intégrations
- **VS Code** : Extension pour visualisation JSONL
- **GitHub Actions** : Workflow d'analyse automatique
- **Docker** : Conteneurisation pour CI/CD
- **Jupyter** : Notebooks d'analyse des résultats

---

**🎉 Vous êtes maintenant prêt à maîtriser le traitement en lot !**

Pour des questions spécifiques ou des cas d'usage avancés, n'hésitez pas à consulter notre [communauté](https://github.com/maximebausset/gitingest-ai/discussions) ou à créer une [issue](https://github.com/maximebausset/gitingest-ai/issues). 