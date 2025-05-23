# Changelog (Advanced Gitingest Fork)

## [Unreleased]

### ✨ New Features
- ✨ Contextual extraction for LLMs (GPT-4, Claude, Gemini, etc.)
- ✨ Modern CLI with dynamic subcommands: `gitingest ai <model>`
- ✨ Progress bar (`tqdm`) during file processing
- ✨ Parallel file reading (ThreadPoolExecutor)
- ✨ Strict allowlist for critical infra/config files

### ♻️ Refactoring
- ♻️ Centralized LLM/configuration and classification rules in YAML
- ♻️ Refactored and strongly-typed business modules (classification, extraction, formatting, utils)

### 🐛 Bug Fixes
- 🐛 Correct allowlist handling and artifact exclusion
- 🐛 Improved symlink and duplicate management
- 🐛 Output files now created in the current directory by default

### 🚀 Performance
- 🚀 Parallelization and live progress bar for fast processing
- 🚀 Detailed logs and diagnostics for bottleneck analysis

### ✅ Tests
- ✅ Extensive unit, CLI, and integration tests
- ✅ High coverage and robust test structure

### 🚀 Performance & UX
- 🚀 Nettoyage des logs et option d'activation du debug
- 🚀 Nettoyage de la solution (suppression des caches, artefacts, etc.)
- 🚀 Correction de la logique d'output IA (création dans le répertoire courant)
- 🚀 Affichage temps réel de la barre de progression
- 🚀 Ajout de logs détaillés pour le diagnostic

### 📝 Documentation
- 📝 Mise à jour du README avec les nouveautés, bonnes pratiques et conventions gitmoji
- 📝 Ajout d'exemples de messages de commit et de versioning sémantique 