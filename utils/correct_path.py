import logging
from pathlib import Path

from utils.datatypes import ValidatedPath

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def get_path(path: str) -> ValidatedPath:
    """Create full absolute path and verify existence"""
    new_path = PROJECT_ROOT / path

    if not new_path.exists():
        logger.warning("Path doesn't exist yet: %s", new_path)
    else:
        logger.info("Absolute path confirmed: %s", new_path)

    return ValidatedPath(new_path)