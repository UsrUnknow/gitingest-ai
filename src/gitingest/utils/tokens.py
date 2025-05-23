"""Utilitaires pour le comptage et la gestion des tokens dans le contexte LLM."""

from typing import List
import tiktoken


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Compte précisément le nombre de tokens dans un texte avec tiktoken.

    Paramètres
    ----------
    text : str
        Le texte à analyser.
    encoding_name : str
        Le nom de l'encodage tiktoken à utiliser (par défaut : cl100k_base).

    Retourne
    -------
    int
        Le nombre de tokens dans le texte.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text, disallowed_special=()))


def truncate_content(text: str, max_tokens: int, strategy: str = "end", encoding_name: str = "cl100k_base") -> str:
    """
    Tronque intelligemment un texte pour ne pas dépasser un nombre de tokens donné.

    Stratégies disponibles :
    - "end" (par défaut) : conserve le début du texte
    - "start" : conserve la fin du texte
    - "middle" : conserve le début et la fin, coupe au milieu

    Paramètres
    ----------
    text : str
        Le texte à tronquer.
    max_tokens : int
        Nombre maximal de tokens à conserver.
    strategy : str
        Stratégie de troncature ('end', 'start', 'middle').
    encoding_name : str
        Encodage tiktoken à utiliser.

    Retourne
    -------
    str
        Le texte tronqué.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    tokens = encoding.encode(text, disallowed_special=())
    n = len(tokens)
    if n <= max_tokens:
        return text
    if strategy == "end":
        return encoding.decode(tokens[:max_tokens])
    elif strategy == "start":
        return encoding.decode(tokens[-max_tokens:])
    elif strategy == "middle":
        half = max_tokens // 2
        return encoding.decode(tokens[:half] + tokens[-(max_tokens - half):])
    else:
        raise ValueError(f"Stratégie inconnue : {strategy}")


def estimate_context_tokens(texts: List[str], encoding_name: str = "cl100k_base") -> int:
    """
    Estime le nombre total de tokens pour une liste de textes (ex : contexte multi-fichiers).

    Paramètres
    ----------
    texts : List[str]
        Liste de textes à analyser.
    encoding_name : str
        Encodage tiktoken à utiliser.

    Retourne
    -------
    int
        Nombre total de tokens pour l'ensemble du contexte.
    """
    encoding = tiktoken.get_encoding(encoding_name)
    return sum(len(encoding.encode(text, disallowed_special=())) for text in texts) 