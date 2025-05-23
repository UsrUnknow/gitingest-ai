# Changelog

## [Unreleased]

### ✨ Nouvelles fonctionnalités
- ✨ Extraction contextuelle priorisée pour LLM (GPT-4, Claude, Gemini, etc.)
- ✨ CLI modernisée avec sous-commandes dynamiques : `gitingest ai <modèle>`
- ✨ Barre de progression (`tqdm`) lors du traitement des fichiers
- ✨ Parallélisation de la lecture des fichiers (ThreadPoolExecutor)
- ✨ Allowlist stricte pour l'inclusion des fichiers critiques d'infra/config

### ♻️ Refactorisation
- ♻️ Centralisation de la configuration LLM et des règles de classification dans des fichiers YAML
- ♻️ Factorisation et typage des modules métiers (classification, extraction, formatting, utils)

### 🐛 Corrections de bugs
- 🐛 Correction de la gestion des allowlist et de l'exclusion des artefacts
- 🐛 Correction de la génération dynamique des sous-commandes
- 🐛 Correction de la logique de découpage IA et de l'inclusion des fichiers critiques dans le contexte

### 🚀 Performance & UX
- 🚀 Nettoyage des logs et option d'activation du debug
- 🚀 Nettoyage de la solution (suppression des caches, artefacts, etc.)
- 🚀 Correction de la logique d'output IA (création dans le répertoire courant)
- 🚀 Affichage temps réel de la barre de progression
- 🚀 Ajout de logs détaillés pour le diagnostic

### 📝 Documentation
- 📝 Mise à jour du README avec les nouveautés, bonnes pratiques et conventions gitmoji
- 📝 Ajout d'exemples de messages de commit et de versioning sémantique 