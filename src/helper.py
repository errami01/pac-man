import os
import sys
from typing import Dict


def get_resource_path(relative_path: str) -> str:
    """ Get absolute path to resource, works for
      dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def validate_loaded_scores(hightscores: Dict[str, int]) -> Dict[str, int]:
    for name, score in hightscores.items():
        if (not isinstance(score, int)) or (score < 0):
            print(f"WARNING: Invalid score value for player {name}")
            hightscores[name] = 0
    return hightscores
