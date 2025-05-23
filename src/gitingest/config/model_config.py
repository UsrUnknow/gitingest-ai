"""Configurations spécifiques pour différents modèles LLM et gestion des types de fichiers importants."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import yaml
import os
import logging

# Constantes pour les types de fichiers et leur importance
IMPORTANT_FILE_TYPES = [
    ".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c", ".h", ".json", ".yaml", ".yml", ".md", ".txt",".cs",".php",".html",".css",".sql",".rb",".swift",".kt",".scala",".groovy",".bash",".sh",".zsh",".fish",".ps1",".psm1",".psd1",".psd2",".psd3",".psd4",".psd5",".psd6",".psd7",".psd8",".psd9",".psd10"
]

CONFIG_FILES_PRIORITY = [
    "pyproject.toml", "requirements.txt", "package.json", "Dockerfile", "Makefile", "setup.py", "environment.yml"
]

@dataclass
class LLMModelConfig:
    """
    Configuration pour un modèle LLM spécifique.

    Attributs
    ----------
    max_tokens : int
        Nombre maximal de tokens autorisés pour une requête.
    max_file_size : int
        Taille maximale d'un fichier à traiter (en octets).
    prioritize_config_files : bool
        Indique si les fichiers de configuration doivent être prioritaires dans l'analyse.
    important_file_types : Optional[List[str]]
        Liste des extensions de fichiers considérés comme importants.
    config_files_priority : Optional[List[str]]
        Liste des fichiers de configuration à prioriser.
    additional_params : Optional[dict]
        Paramètres additionnels spécifiques au modèle.
    """
    max_tokens: int
    max_file_size: int
    prioritize_config_files: bool = True
    important_file_types: Optional[List[str]] = field(default_factory=lambda: IMPORTANT_FILE_TYPES)
    config_files_priority: Optional[List[str]] = field(default_factory=lambda: CONFIG_FILES_PRIORITY)
    additional_params: Optional[dict] = field(default_factory=dict)


DEFAULT_MODEL_CONFIGS: Dict[str, LLMModelConfig] = {
    # OpenAI
    "gpt-4": LLMModelConfig(
        max_tokens=8192,
        max_file_size=5 * 1024 * 1024,  # 5 MB
    ),
    "gpt-4-32k": LLMModelConfig(
        max_tokens=32768,
        max_file_size=10 * 1024 * 1024,  # 10 MB
    ),
    "gpt-4-turbo": LLMModelConfig(
        max_tokens=128_000,
        max_file_size=20 * 1024 * 1024,  # 20 MB
    ),
    "gpt-4o": LLMModelConfig(
        max_tokens=128_000,
        max_file_size=20 * 1024 * 1024,  # 20 MB
    ),
    "gpt-4o-mini": LLMModelConfig(
        max_tokens=128_000,
        max_file_size=20 * 1024 * 1024,  # 20 MB
    ),
    "gpt-4.5": LLMModelConfig(
        max_tokens=128_000,
        max_file_size=20 * 1024 * 1024,  # 20 MB
    ),
    "o1": LLMModelConfig(
        max_tokens=200_000,
        max_file_size=40 * 1024 * 1024,  # 40 MB
    ),
    "o3-mini": LLMModelConfig(
        max_tokens=200_000,
        max_file_size=40 * 1024 * 1024,  # 40 MB
    ),
    "o1-mini": LLMModelConfig(
        max_tokens=128_000,
        max_file_size=20 * 1024 * 1024,  # 20 MB
    ),
    "gpt-3.5-turbo": LLMModelConfig(
        max_tokens=16_384,
        max_file_size=2 * 1024 * 1024,  # 2 MB
    ),
    "gpt-3.5-turbo-instruct": LLMModelConfig(
        max_tokens=4096,
        max_file_size=1 * 1024 * 1024,  # 1 MB
    ),
    # Anthropic Claude
    "claude-3-opus": LLMModelConfig(
        max_tokens=200_000,
        max_file_size=40 * 1024 * 1024,  # 40 MB
    ),
    "claude-3-sonnet": LLMModelConfig(
        max_tokens=200_000,
        max_file_size=40 * 1024 * 1024,  # 40 MB
    ),
    "claude-3-haiku": LLMModelConfig(
        max_tokens=200_000,
        max_file_size=40 * 1024 * 1024,  # 40 MB
    ),
    "claude-3.5-sonnet": LLMModelConfig(
        max_tokens=200_000,
        max_file_size=40 * 1024 * 1024,  # 40 MB
    ),
    "claude-3.5-haiku": LLMModelConfig(
        max_tokens=200_000,
        max_file_size=40 * 1024 * 1024,  # 40 MB
    ),
    # Google Gemini
    "gemini-1.5-pro": LLMModelConfig(
        max_tokens=2_000_000,
        max_file_size=200 * 1024 * 1024,  # 200 MB
    ),
    "gemini-1.5-flash": LLMModelConfig(
        max_tokens=1_000_000,
        max_file_size=100 * 1024 * 1024,  # 100 MB
    ),
    "gemini-2.0-flash": LLMModelConfig(
        max_tokens=1_000_000,
        max_file_size=100 * 1024 * 1024,  # 100 MB
    ),
    # Meta Llama
    "llama-3-70b": LLMModelConfig(
        max_tokens=128_000,
        max_file_size=20 * 1024 * 1024,  # 20 MB
    ),
    "llama-3-8b": LLMModelConfig(
        max_tokens=8_192,
        max_file_size=2 * 1024 * 1024,  # 2 MB
    ),
    # Mistral
    "mistral-large": LLMModelConfig(
        max_tokens=128_000,
        max_file_size=20 * 1024 * 1024,  # 20 MB
    ),
    "mistral-small": LLMModelConfig(
        max_tokens=32_000,
        max_file_size=5 * 1024 * 1024,  # 5 MB
    ),
    "mixtral-8x7b": LLMModelConfig(
        max_tokens=32_000,
        max_file_size=5 * 1024 * 1024,  # 5 MB
    ),
    # Cohere
    "command-r+": LLMModelConfig(
        max_tokens=128_000,
        max_file_size=20 * 1024 * 1024,  # 20 MB
    ),
    # DeepSeek
    "deepseek-r1": LLMModelConfig(
        max_tokens=128_000,
        max_file_size=20 * 1024 * 1024,  # 20 MB
    ),
    # Genspark
    "genspark": LLMModelConfig(
        max_tokens=128_000,
        max_file_size=2 * 1024 * 1024,  # 2 MB
    ),
} 

LLM_MODELS_YAML = os.path.join(os.path.dirname(__file__), "llm_models.yaml")

def load_llm_model_configs() -> Dict[str, LLMModelConfig]:
    """
    Charge dynamiquement les presets LLM depuis le fichier YAML. Fallback sur les presets codés en dur si le fichier n'existe pas.
    Valide la présence des champs obligatoires et loggue les erreurs.
    """
    logger = logging.getLogger("gitingest.config")
    if not os.path.exists(LLM_MODELS_YAML):
        return DEFAULT_MODEL_CONFIGS
    with open(LLM_MODELS_YAML, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    configs = {}
    for key, val in data.items():
        if not isinstance(val, dict) or "max_tokens" not in val or "max_file_size" not in val:
            logger.warning(f"Preset LLM '{key}' invalide ou incomplet (doit contenir 'max_tokens' et 'max_file_size'). Ignoré.")
            continue
        try:
            configs[key] = LLMModelConfig(
                max_tokens=val["max_tokens"],
                max_file_size=val["max_file_size"],
                additional_params={k: v for k, v in val.items() if k not in ("max_tokens", "max_file_size")}
            )
        except Exception as e:
            logger.error(f"Erreur lors de la création du preset LLM '{key}': {e}")
    if not configs:
        logger.error("Aucun preset LLM valide trouvé dans le YAML, fallback sur les presets codés en dur.")
        return DEFAULT_MODEL_CONFIGS
    return configs

# Utilisation par défaut
MODEL_CONFIGS = load_llm_model_configs() 