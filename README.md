# Gitingest

[![Image](./docs/frontpage.png "Gitingest main page")](https://gitingest.com)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/cyclotruc/gitingest/blob/main/LICENSE)
[![PyPI version](https://badge.fury.io/py/gitingest.svg)](https://badge.fury.io/py/gitingest)
[![GitHub stars](https://img.shields.io/github/stars/cyclotruc/gitingest?style=social.svg)](https://github.com/cyclotruc/gitingest)
[![Downloads](https://pepy.tech/badge/gitingest)](https://pepy.tech/project/gitingest)

[![Discord](https://dcbadge.limes.pink/api/server/https://discord.com/invite/zerRaGK9EC)](https://discord.com/invite/zerRaGK9EC)

Turn any Git repository into a prompt-friendly text ingest for LLMs.

You can also replace `hub` with `ingest` in any GitHub URL to access the corresponding digest.

[gitingest.com](https://gitingest.com) · [Chrome Extension](https://chromewebstore.google.com/detail/adfjahbijlkjfoicpjkhjicpjpjfaood) · [Firefox Add-on](https://addons.mozilla.org/firefox/addon/gitingest)

# ⚡ Gitingest AI (Advanced Fork)

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PyPI version](https://badge.fury.io/py/gitingest.svg)](https://pypi.org/project/gitingest/)
[![GitHub stars](https://img.shields.io/github/stars/cyclotruc/gitingest?style=social.svg)](https://github.com/cyclotruc/gitingest)

> **Fork of the original [Gitingest](https://github.com/arthurhenry/gitingest)** — this version brings advanced file selection, LLM context extraction, a modern CLI, and developer-focused improvements.

---

## 📦 Installation
```bash
pip install gitingest
# or
pipx install gitingest
```

---

## 🚀 Features
- Fine-grained allowlist/ignore management (pathspec, always-include logic)
- Modern CLI with dynamic subcommands and LLM model selection
- Contextual extraction for LLMs (GPT-4, Claude, Gemini, etc.)
- Progress bar and live logs (tqdm)
- Parallel file reading for performance
- Robust artifact/cache exclusion and config file inclusion
- Extensive tests and improved developer experience
- Compatible with any language or project structure

---

## 💡 Usage

### Command Line & LLM Extraction
```bash
# Analyze a local directory or remote repo
gitingest /path/to/directory
gitingest https://github.com/user/repo

# LLM context extraction (Markdown output for GPT-4o)
gitingest ai-context --model gpt-4o --format markdown --output context.md

# See all options
gitingest --help
gitingest ai-context --help
```

### Python API
```python
from gitingest import ingest, ingest_async
summary, tree, content = ingest("/path/to/directory")
# Async
import asyncio
result = asyncio.run(ingest_async("/path/to/directory"))
```

---

## 🐳 Self-host
```bash
docker build -t gitingest .
docker run -d --name gitingest -p 8000:8000 gitingest
```
App available at `http://localhost:8000`.

---

## 🤝 Contribution
- Use **atomic commits** and [gitmoji](https://gitmoji.dev/) for commit messages
- See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines
- Respect the original project's spirit while bringing advanced improvements

---

## 🛠️ Stack
- [FastAPI](https://github.com/fastapi/fastapi) — backend
- [Jinja2](https://jinja.palletsprojects.com) — templating
- [Tailwind CSS](https://tailwindcss.com) — frontend
- [tiktoken](https://github.com/openai/tiktoken) — token estimation
- [posthog](https://github.com/PostHog/posthog) — analytics

---

## 📝 Changelog
See [CHANGELOG.md](docs/CHANGELOG.md) for a detailed list of changes.

---

## 📄 License
MIT — see [LICENSE](LICENSE)

---

## 🙏 Credits
- Original project: [Gitingest by arthurhenry](https://github.com/arthurhenry/gitingest)
- This fork: advanced features, LLM context, CLI, and developer experience by [your name or org]

## 🚀 Features

- **Easy code context**: Get a text digest from a Git repository URL or a directory
- **Smart Formatting**: Optimized output format for LLM prompts
- **Statistics about**:
  - File and directory structure
  - Size of the extract
  - Token count
- **CLI tool**: Run it as a shell command
- **Python package**: Import it in your code

## 📚 Requirements

- Python 3.7+

## 🧩 Browser Extension Usage

<!-- markdownlint-disable MD033 -->
<a href="https://chromewebstore.google.com/detail/adfjahbijlkjfoicpjkhjicpjpjfaood" target="_blank" title="Get Gitingest Extension from Chrome Web Store"><img height="48" src="https://github.com/user-attachments/assets/20a6e44b-fd46-4e6c-8ea6-aad436035753" alt="Available in the Chrome Web Store" /></a>
<a href="https://addons.mozilla.org/firefox/addon/gitingest" target="_blank" title="Get Gitingest Extension from Firefox Add-ons"><img height="48" src="https://github.com/user-attachments/assets/c0e99e6b-97cf-4af2-9737-099db7d3538b" alt="Get The Add-on for Firefox" /></a>
<a href="https://microsoftedge.microsoft.com/addons/detail/nfobhllgcekbmpifkjlopfdfdmljmipf" target="_blank" title="Get Gitingest Extension from Microsoft Edge Add-ons"><img height="48" src="https://github.com/user-attachments/assets/204157eb-4cae-4c0e-b2cb-db514419fd9e" alt="Get from the Edge Add-ons" /></a>
<!-- markdownlint-enable MD033 -->

The extension is open source at [lcandy2/gitingest-extension](https://github.com/lcandy2/gitingest-extension).

Issues and feature requests are welcome to the repo.

## 🤝 Contributing

### Non-technical ways to contribute

- **Create an Issue**: If you find a bug or have an idea for a new feature, please [create an issue](https://github.com/cyclotruc/gitingest/issues/new) on GitHub. This will help us track and prioritize your request.
- **Spread the Word**: If you like Gitingest, please share it with your friends, colleagues, and on social media. This will help us grow the community and make Gitingest even better.
- **Use Gitingest**: The best feedback comes from real-world usage! If you encounter any issues or have ideas for improvement, please let us know by [creating an issue](https://github.com/cyclotruc/gitingest/issues/new) on GitHub or by reaching out to us on [Discord](https://discord.com/invite/zerRaGK9EC).

### Technical ways to contribute

Gitingest aims to be friendly for first time contributors, with a simple Python and HTML codebase. If you need any help while working with the code, reach out to us on [Discord](https://discord.com/invite/zerRaGK9EC). For detailed instructions on how to make a pull request, see [CONTRIBUTING.md](./CONTRIBUTING.md).

## 🛠️ Stack

- [Tailwind CSS](https://tailwindcss.com) - Frontend
- [FastAPI](https://github.com/fastapi/fastapi) - Backend framework
- [Jinja2](https://jinja.palletsprojects.com) - HTML templating
- [tiktoken](https://github.com/openai/tiktoken) - Token estimation
- [posthog](https://github.com/PostHog/posthog) - Amazing analytics

### Looking for a JavaScript/FileSystemNode package?

Check out the NPM alternative 📦 Repomix: <https://github.com/yamadashy/repomix>

## 🚀 Project Growth

[![Star History Chart](https://api.star-history.com/svg?repos=cyclotruc/gitingest&type=Date)](https://star-history.com/#cyclotruc/gitingest&Date)

## 🤖 Optimisation pour LLM (Large Language Models)

Gitingest propose désormais une extraction intelligente et un formatage optimisé pour l'ingestion par les LLM modernes (GPT-4, Claude, Gemini, Mistral, etc.).

### Fonctionnalités principales
- **Extraction contextuelle priorisée** : sélectionne et tronque les fichiers les plus pertinents selon le modèle LLM choisi (config, doc, source, etc.)
- **Gestion automatique de la limite de tokens** : ne dépasse jamais la capacité du modèle
- **Formatage optimisé** : sortie en Markdown (spécial LLM), JSON ou texte brut
- **Support multi-modèles** : GPT-4, GPT-4o, Claude 3, Gemini, Mistral, Llama, Cohere, Genspark, etc.

### Utilisation de la commande `ai-context`

```bash
# Extraction optimisée pour GPT-4o, format Markdown
$ gitingest ai-context --model gpt-4o --format markdown --output context.md

# Extraction pour Claude 3 Sonnet, format JSON
$ gitingest ai-context --model claude-3-sonnet --format json

# Limiter à 20 fichiers, sans contenu, métadonnées uniquement
$ gitingest ai-context --model mistral-large --max-files 20 --no-content --show-metadata
```

#### Options principales
- `--model` : nom du modèle LLM (voir liste ci-dessous)
- `--format` : format de sortie (`markdown`, `json`, `text`)
- `--output` : chemin du fichier de sortie (stdout par défaut)
- `--max-files` : nombre maximal de fichiers à inclure
- `--show-metadata/--no-metadata` : afficher ou non les métadonnées
- `--show-content/--no-content` : afficher ou non le contenu des fichiers

### Modèles LLM supportés et limites principales

| Modèle              | Limite tokens | Taille max fichier |
|---------------------|---------------|-------------------|
| gpt-4               | 8 192         | 5 Mo              |
| gpt-4o              | 128 000       | 20 Mo             |
| gpt-4-turbo         | 128 000       | 20 Mo             |
| claude-3-sonnet     | 200 000       | 40 Mo             |
| claude-3-opus       | 200 000       | 40 Mo             |
| gemini-1.5-pro      | 2 000 000     | 200 Mo            |
| mistral-large       | 128 000       | 20 Mo             |
| llama-3-70b         | 128 000       | 20 Mo             |
| cohere command-r+   | 128 000       | 20 Mo             |
| genspark            | 128 000       | 2 Mo              |
| ...                 | ...           | ...               |

> La liste complète et à jour est disponible via `gitingest ai-context --help`.

### Conseils d'optimisation
- **Choisissez le modèle adapté** : plus le contexte/token limit est grand, plus vous pouvez extraire de fichiers et de contenu.
- **Utilisez `--max-files` pour limiter la taille** si vous ciblez un modèle avec une petite fenêtre de contexte.
- **Désactivez l'affichage du contenu** (`--no-content`) pour obtenir un aperçu structurel rapide.
- **Privilégiez le format Markdown** pour l'ingestion LLM (structure hiérarchique, code fences, métadonnées explicites).
- **Adaptez la granularité** : pour les très gros dépôts, commencez par n'extraire que les fichiers de configuration et documentation.

Pour toute question ou suggestion, ouvrez une issue ou rejoignez-nous sur [Discord](https://discord.com/invite/zerRaGK9EC) !

## 📝 Changements récents et bonnes pratiques

### Refactorisation et robustesse
- Centralisation de la configuration LLM et des règles de classification dans des fichiers YAML.
- Modules métiers typés, documentés, factorisés.
- CLI modernisée : toutes les commandes LLM sont regroupées sous `gitingest ai <modèle> ...` avec génération dynamique des sous-commandes.
- Structure de tests complète (unitaires, CLI, intégration) avec une couverture élevée.
- Correction de bugs sur la génération dynamique des sous-commandes, la logique de découpage IA, et l'inclusion des fichiers critiques dans le contexte.

### Nettoyage, performance et UX
- Nettoyage des logs : suppression des logs verbeux, conservation des logs critiques et option d'activation du debug.
- Nettoyage de la solution : suppression des fichiers `.log`, des caches (`.mypy_cache`, `.pytest_cache`, etc.), et des artefacts temporaires.
- Correction de la logique d'output IA : les fichiers de sortie sont désormais créés dans le répertoire courant (là où la commande est lancée), sauf si un chemin est explicitement spécifié.
- Ajout d'une logique pour remplacer les fichiers d'output existants.
- Ajout d'une barre de progression (`tqdm`) lors du traitement des fichiers, désactivable avec `--no-progress`.
- Parallélisation de la lecture des fichiers avec `ThreadPoolExecutor` (8 threads), logs enrichis (début/fin, erreurs, temps de traitement, nombre de fichiers), et progression live.
- Correction pour que la barre de progression s'affiche en temps réel (utilisation de `executor.map` au lieu de `as_completed`).
- Ajout de logs détaillés pour diagnostiquer les blocages éventuels.

### Gestion avancée des fichiers ignorés et artefacts
- Intégration de la bibliothèque `pathspec` pour filtrer les fichiers/dossiers selon le `.gitignore`.
- Si pas de `.gitignore`, exclusion automatique des fichiers/dossiers générés courants (caches, artefacts, logs, etc.).
- Ajout d'une allowlist stricte : seuls les fichiers de config/infra typiques sont inclus, et uniquement s'ils sont à la racine ou dans un dossier standard (`.github`, `config`, `.gitlab`).
- Exclusion explicite de tous les fichiers dans des dossiers de cache/artefact, même si leur nom matche la allowlist.
- Solution générique, compatible avec tous les langages et architectures de projet.

### Bonnes pratiques de contribution
- Utilisez des commits atomiques et explicites.
- Adoptez la convention [gitmoji](https://gitmoji.dev/) pour vos messages de commit (ex : `:sparkles: Ajout extraction contextuelle LLM`).
- Privilégiez les PRs courtes et bien documentées.
- Respectez la structure du projet et les conventions de typage/docstring.
