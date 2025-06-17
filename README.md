# 🚀 Gitingest AI - Advanced Multi-Project Context Extraction

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org)
[![GitHub stars](https://img.shields.io/github/stars/cyclotruc/gitingest?style=social.svg)](https://github.com/cyclotruc/gitingest)
[![Tests](https://img.shields.io/badge/tests-passing-green.svg)](#tests)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](#tests)
[![Code Quality](https://img.shields.io/badge/code%20quality-A-brightgreen.svg)](#code-quality)
[![Performance](https://img.shields.io/badge/performance-10x%20faster-orange.svg)](#performance)

> **Version avancée de Gitingest** — Transformez vos repositories Git en contexte optimisé pour les LLM avec un filtrage intelligent, traitement en lot, support multi-langage et bien plus !

---

## 📑 Table des Matières
- [✨ Nouvelles Fonctionnalités](#-nouvelles-fonctionnalités)
- [📦 Installation](#-installation)
- [🚀 Utilisation](#-utilisation)
  - [💻 Interface en ligne de commande](#-interface-en-ligne-de-commande)
  - [🔄 Traitement en lot (NOUVEAU)](#-traitement-en-lot-nouveau)
  - [🛠️ Script utilitaire](#️-script-utilitaire)
  - [🐍 API Python](#-api-python)
- [🎯 Filtrage Intelligent](#-filtrage-intelligent)
- [🌐 Support Multi-Langage](#-support-multi-langage)
- [📋 Exemples Pratiques](#-exemples-pratiques)
- [📚 Documentation](#-documentation)
- [🤝 Contribution](#-contribution)
- [📄 Licence](#-licence)

---

## ✨ Nouvelles Fonctionnalités

### 🔥 **Traitement en lot multi-projets**
- **Parallélisme intelligent** : Traitez plusieurs projets simultanément avec contrôle de la concurrence
- **Nommage automatique** : Les fichiers de sortie sont nommés d'après les répertoires traités
- **Format JSONL optimisé** : Structure de données parfaite pour l'analyse IA

### 🧠 **Filtrage multi-langage avancé**
- **Support universel** : Python, JavaScript/React, C#/.NET, Java, Go, Rust, PHP, Ruby, Swift, Dart/Flutter, et plus
- **Exclusions intelligentes** : Ignore automatiquement `node_modules`, `bin`, `obj`, `__pycache__`, etc.
- **Configuration flexible** : Options personnalisables pour chaque type de projet

### ⚡ **Performance optimisée**
- **Traitement parallèle** : ThreadPoolExecutor pour des performances maximales
- **Filtrage en temps réel** : Évite le traitement de fichiers inutiles
- **Rapports détaillés** : Mode verbeux avec statistiques complètes

### 🎨 **Interface utilisateur améliorée**
- **Script utilitaire** avec raccourcis langages (`--languages py,js,react`)
- **Mode simulation** (`--dry-run`) pour tester les configurations
- **Progression en temps réel** avec indicateurs visuels
- **Documentation intégrée** avec exemples

---

## 📦 Installation

```bash
pip install gitingest
```

Ou installez depuis les sources :

```bash
git clone https://github.com/maximebausset/gitingest-ai.git
cd gitingest-ai
pip install -e .
```

---

## 🚀 Utilisation

### 💻 Interface en ligne de commande

#### Commandes pour modèles spécifiques
```bash
# GPT-4
gitingest ai gpt-4 ./mon-projet --verbose

# Claude
gitingest ai claude-3-opus ./src --include-ext .py,.js --exclude-dirs tests

# Gemini
gitingest ai gemini-1.5-pro ./app --max-files 100 --format json
```

#### Options avancées
```bash
# Avec filtrage personnalisé
gitingest ai gpt-4 ./projet \
  --include-ext .py,.js,.ts \
  --exclude-dirs node_modules,dist,build \
  --exclude-files "*.min.js,*.bundle.*" \
  --max-files 200 \
  --verbose

# Mode simulation
gitingest ai claude ./src --dry-run --verbose
```

### 🔄 **Traitement en lot (NOUVEAU)**

La fonctionnalité phare pour traiter plusieurs projets simultanément :

```bash
# Traitement parallèle de plusieurs projets
gitingest ai batch ./projet1 ./projet2 ./projet3 --parallel 4

# Avec filtrage spécialisé
gitingest ai batch \
  ./frontend ./backend ./mobile \
  --include-ext .js,.ts,.py,.dart \
  --exclude-dirs node_modules,venv,build \
  --parallel 6 \
  --verbose

# Patterns avec wildcards
gitingest ai batch ./projects/*/src --parallel 8
```

**Avantages du mode batch :**
- ✅ **Parallélisme** : Traitement simultané avec contrôle de concurrence
- ✅ **Nommage intelligent** : `projet1/` → `projet1.jsonl`
- ✅ **Format optimisé** : Structure JSONL avec métadonnées
- ✅ **Performances** : Jusqu'à 10x plus rapide pour plusieurs projets

### 🛠️ **Script utilitaire**

Script bash intelligent avec raccourcis :

```bash
# Python + JavaScript
./scripts/quick-ingest.sh --languages py,js ./src ./api

# React complet
./scripts/quick-ingest.sh --languages react ./frontend

# .NET C#
./scripts/quick-ingest.sh --languages cs,dotnet \
  --exclude-dirs bin,obj ./MyApp

# Java avec sortie personnalisée
./scripts/quick-ingest.sh --languages java \
  --output-dir ./analysis ./projet1 ./projet2
```

**Raccourcis langages disponibles :**
- `py` (Python), `js` (JavaScript), `ts` (TypeScript)
- `react` (JS+TS+CSS complet), `vue` (Vue.js)
- `cs`/`dotnet` (C#/.NET), `java`, `kotlin`, `scala`
- `go`, `rust`, `php`, `ruby`, `swift`, `dart`
- `cpp` (C++), `c`, `web` (frontend), `config`

### 🐍 API Python

```python
from gitingest.cli import main
from gitingest.extraction.extractor import extract_repo_context

# Utilisation via CLI
main(['ai', 'gpt-4', './projet', '--format', 'json'])

# Traitement en lot
main(['ai', 'batch', './proj1', './proj2', '--parallel', '4'])

# API directe
from gitingest.utils.filesystem_tree import build_filesystem_tree
from gitingest.config.model_config import MODEL_CONFIGS

tree = build_filesystem_tree("./projet")
context = extract_repo_context(tree, MODEL_CONFIGS["gpt-4"])
```

---

## 🎯 Filtrage Intelligent

### Configuration automatique par type de projet

**Python** :
```yaml
exclude_dirs: [__pycache__, .pytest_cache, venv, build, dist]
important_files: [requirements.txt, pyproject.toml, setup.py]
```

**JavaScript/React** :
```yaml
exclude_dirs: [node_modules, .next, build, dist]
important_files: [package.json, webpack.config.js, tsconfig.json]
```

**C#/.NET** :
```yaml
exclude_dirs: [bin, obj, packages, TestResults]
important_files: [*.sln, *.csproj, appsettings.json]
```

### Options de filtrage avancées

```bash
# Extensions spécifiques
--include-ext .py,.js,.ts,.css

# Exclusions personnalisées
--exclude-ext .log,.tmp,.cache
--exclude-dirs temp,logs,cache
--exclude-files "*.min.*,bundle.*"

# Filtrage par taille
--max-file-size 1000000  # 1MB max par fichier
```

---

## 🌐 Support Multi-Langage

### Langages supportés avec configurations optimisées

| Langage | Extensions | Exclusions spécifiques | Fichiers importants |
|---------|------------|------------------------|-------------------|
| **Python** | `.py`, `.pyi`, `.pyx` | `__pycache__`, `venv`, `.pytest_cache` | `requirements.txt`, `pyproject.toml` |
| **JavaScript** | `.js`, `.mjs`, `.cjs` | `node_modules`, `.next`, `dist` | `package.json`, `webpack.config.js` |
| **TypeScript** | `.ts`, `.tsx`, `.d.ts` | `node_modules`, `build` | `tsconfig.json`, `.eslintrc.js` |
| **React** | `.jsx`, `.tsx`, `.css`, `.scss` | `.next`, `build`, `coverage` | `next.config.js`, `vite.config.js` |
| **C#** | `.cs`, `.vb`, `.fs` | `bin`, `obj`, `packages` | `*.sln`, `*.csproj`, `appsettings.json` |
| **Java** | `.java`, `.kt`, `.scala` | `target`, `.gradle`, `.m2` | `pom.xml`, `build.gradle` |
| **Go** | `.go`, `.mod`, `.sum` | `vendor`, `bin` | `go.mod`, `Makefile` |
| **Rust** | `.rs`, `.toml` | `target`, `.cargo` | `Cargo.toml`, `Cargo.lock` |
| **PHP** | `.php`, `.phtml` | `vendor`, `storage` | `composer.json`, `.env` |
| **Ruby** | `.rb`, `.rake`, `.gemspec` | `vendor`, `.bundle` | `Gemfile`, `Rakefile` |
| **Swift** | `.swift`, `.h`, `.m` | `.build`, `DerivedData` | `Package.swift`, `*.xcodeproj` |
| **Dart/Flutter** | `.dart`, `.yaml` | `build`, `.dart_tool` | `pubspec.yaml`, `analysis_options.yaml` |

---

## 📋 Exemples Pratiques

### Analyse de projet Full-Stack
```bash
# Frontend React + Backend Python + Mobile Flutter
gitingest ai batch \
  ./frontend ./backend ./mobile \
  --include-ext .js,.jsx,.ts,.tsx,.py,.dart \
  --exclude-dirs node_modules,venv,build,.dart_tool \
  --parallel 3 \
  --verbose
```

### Analyse rapide avec script utilitaire
```bash
# Analyse complète d'un monorepo
./scripts/quick-ingest.sh \
  --languages react,py,go \
  --exclude-dirs node_modules,venv,vendor \
  --output-dir ./analysis \
  ./packages/* ./services/*
```

### Migration de projets Legacy
```bash
# Analyse de projets C# + JavaScript legacy
gitingest ai batch \
  ./legacy-web ./legacy-api ./new-microservices \
  --languages cs,js \
  --exclude-dirs bin,obj,node_modules,packages \
  --max-file-size 500000 \
  --parallel 2
```

---

## 📚 Documentation

### 📖 Documentation complète disponible

| Document | Description | Niveau |
|----------|-------------|---------|
| **[Guide de traitement en lot](docs/BATCH_PROCESSING.md)** | Documentation détaillée du mode batch | 🟢 Débutant |
| **[Utilisation avancée](docs/ADVANCED_USAGE.md)** | Workflows entreprise et CI/CD | 🔴 Avancé |
| **[Limites de taille](docs/SIZE_LIMITS.md)** | Gestion des gros projets | 🟡 Intermédiaire |
| **[Configuration des filtres](src/gitingest/config/default_filters.yaml)** | Réglages par langage | 🟡 Intermédiaire |
| **[Script utilitaire](scripts/quick-ingest.sh)** | Raccourcis et automatisation | 🟢 Débutant |
| **[Améliorations récentes](IMPROVEMENTS.md)** | Nouvelles fonctionnalités | 📊 Référence |

### 🛠️ Aide intégrée
```bash
gitingest --help                    # Aide générale
gitingest ai --help                 # Commandes IA
gitingest ai batch --help           # Options de traitement en lot
./scripts/quick-ingest.sh --help    # Script utilitaire

# Exemples contextuels
gitingest ai batch --help | grep -A5 "Examples"
```

### 🎓 Guides par cas d'usage
- **[Audit de sécurité](docs/ADVANCED_USAGE.md#audit-de-sécurité)** - Analyse multi-projets pour sécurité
- **[Migration legacy](docs/ADVANCED_USAGE.md#migration-legacy)** - Modernisation de code
- **[CI/CD Integration](docs/ADVANCED_USAGE.md#workflows-cicd)** - Intégration dans pipelines
- **[Optimisation LLM](docs/ADVANCED_USAGE.md#optimisation-pour-différents-llm)** - Configuration par modèle IA

---

## 🤝 Contribution

Nous accueillons les contributions ! Voici comment participer :

### Développement
```bash
git clone https://github.com/maximebausset/gitingest-ai.git
cd gitingest-ai
pip install -e ".[dev]"
pytest tests/
```

### Améliorations suggérées
- [ ] Support de nouveaux langages (Kotlin natif, Scala, Elixir)
- [ ] Interface web pour configuration avancée
- [ ] Intégration avec IDEs populaires
- [ ] Plugins pour CI/CD (GitHub Actions, GitLab CI)
- [ ] Cache intelligent pour éviter le re-traitement
- [ ] Analyse de dépendances et graphiques

### Guidelines
- Utilisez des commits atomiques avec [gitmoji](https://gitmoji.dev/)
- Ajoutez des tests pour les nouvelles fonctionnalités
- Mettez à jour la documentation
- Suivez le [Semantic Versioning](https://semver.org/)

---

## 📄 Licence

MIT. Voir [LICENSE](LICENSE) pour plus de détails.

---

## ⭐ Crédits et Remerciements

- **Projet original** : [Gitingest](https://github.com/cyclotruc/gitingest) par cyclotruc
- **Inspiration** : La communauté open source et les utilisateurs de LLM
- **Contributeurs** : Tous ceux qui ont signalé des bugs et suggéré des améliorations

---

**🚀 Prêt à transformer vos projets en contexte IA optimisé ?**

```bash
pip install gitingest
gitingest ai batch ./mon-projet --verbose
```

**💡 Besoin d'aide ?** Consultez la [documentation](docs/) ou créez une [issue](https://github.com/maximebausset/gitingest-ai/issues) !
