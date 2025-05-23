import logging
import sys

def setup_logger(name: str = "gitingest", level: int = logging.INFO) -> logging.Logger:
    """
    Configure et retourne un logger prêt à l'emploi pour le projet.

    Paramètres
    ----------
    name : str
        Nom du logger (par défaut: 'gitingest').
    level : int
        Niveau de log (logging.DEBUG, logging.INFO, etc.).

    Retourne
    -------
    logging.Logger
        Logger configuré.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger

# Logger global par défaut
logger = setup_logger() 