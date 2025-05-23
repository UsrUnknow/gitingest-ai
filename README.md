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

## 📑 Table of Contents
- [✨ Features](#-features)
- [📦 Installation](#-installation)
- [🚀 Usage](#-usage)
  - [💻 Command-line (CLI)](#-command-line-cli)
  - [🐍 Python API](#-python-api)
  - [🤖 LLM Context Extraction](#-llm-context-extraction)
- [🐳 Self-host](#-self-host)
- [🛠️ Stack](#️-stack)
- [📝 Changelog](#-changelog)
- [📈 Project Growth](#-project-growth)
- [🤝 Contributing](#-contributing)
- [🪪 License](#-license)
- [⭐ Credits](#-credits)

---

## ✨ Features

- **Advanced file selection**: Fine-grained allowlist/ignore management (pathspec, always-include logic, critical infra/config detection)
- **Modern CLI**: Dynamic subcommands, LLM model selection, ergonomic options
- **Contextual extraction for LLMs**: Optimized for GPT-4, Claude, Gemini, etc. (token limits, file prioritization, chunking)
- **Progress bar & live logs**: Real-time feedback with `tqdm`, detailed logging, debug options
- **Parallel file reading**: Fast context extraction using ThreadPoolExecutor
- **Robust output management**: Outputs always written to the current working directory, with smart chunking and JSONL format
- **Extensive test suite**: High coverage, CLI/integration/unit tests, regression protection
- **Cross-language support**: Works for Python, JS, Java, C#, Go, Rust, React, and more
- **Self-host ready**: Docker, CI/CD, and config best practices

---

## 📦 Installation

```bash
pip install gitingest
```

Or clone and install locally:

```bash
git clone https://github.com/UsrUnknow/gitingest-ai.git
cd gitingest-ai
pip install -e .
```

---

## 🚀 Usage

### 💻 Command-line (CLI)

Extract optimized context for LLMs:

```bash
gitingest ai <model> <source_dir> [options]
```

**Examples:**
```bash
gitingest ai gpt-4 ./my-project --format markdown --output context.md
gitingest ai claude ./src --max-files 50 --dry-run
gitingest ai gpt-4 . --audit --log-level debug
```

**Main options:**
- `--format` (markdown, json, text)
- `--output` (output file path)
- `--max-files` (max files in context)
- `--show-metadata/--no-metadata`
- `--show-content/--no-content`
- `--audit` (detailed extraction report)
- `--dry-run` (no file written)
- `--log-level` (debug, info, warning, error)
- `--no-progress` (disable progress bar)

### 🐍 Python API

```python
from gitingest.cli import cli
cli(["ai", "gpt-4", "./my-project", "--format", "json"])
```

Or use the extraction logic directly:

```python
from gitingest.extraction.extractor import extract_repo_context
from gitingest.utils.filesystem_tree import build_filesystem_tree
from gitingest.config.model_config import MODEL_CONFIGS

root_node = build_filesystem_tree("./my-project")
repo_context = extract_repo_context(root_node, MODEL_CONFIGS["gpt-4"])
```

### 🤖 LLM Context Extraction

- **Optimized for LLMs**: Context is chunked, prioritized, and formatted for large language models (GPT-4, Claude, Gemini, etc.)
- **Critical files always included**: Dockerfile, requirements.txt, Makefile, etc. are never ignored
- **Smart chunking**: Output split into JSONL files, each respecting model token/file size limits
- **Progressive extraction**: Real-time progress bar and logs

---

## 🐳 Self-host

- **Docker**: Use the provided Dockerfile for easy deployment
- **CI/CD**: Ready-to-use GitHub Actions workflows for tests and publishing
- **Config**: All model/rule configs are centralized in YAML for easy extension

---

## 🛠️ Stack

- Python 3.8+
- Click (CLI)
- tqdm (progress bar)
- pathspec (gitignore support)
- Pytest (tests)
- Docker, GitHub Actions (CI/CD)

---

## 📝 Changelog

See [docs/CHANGELOG.md](docs/CHANGELOG.md) for a detailed list of changes and features.

---

## 📈 Project Growth

- **High test coverage**: Extensive unit, CLI, and integration tests
- **Active maintenance**: Frequent updates, bugfixes, and improvements
- **Open to contributions**: See below for guidelines

---

## 🤝 Contributing

- **Atomic commits**: Each commit should represent a single logical change
- **Use [gitmoji](https://gitmoji.dev/)**: Prefix commits with an emoji for clarity
- **Semantic versioning**: Follow [semver](https://semver.org/)
- **PRs welcome**: Fork, branch, test, and submit a pull request
- **Respect the spirit of the original project**: This fork extends, but does not break, the core philosophy of [Gitingest](https://github.com/arthurhenry/gitingest)

---

## 🪪 License

MIT. See [LICENSE](LICENSE).

## ⭐ Credits

- Original project: [Gitingest](https://github.com/arthurhenry/gitingest)
- Fork & advanced features: [cyclotruc/gitingest-ai](https://github.com/UsrUnknow/gitingest-ai)
