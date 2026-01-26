from __future__ import annotations

import sys
from pathlib import Path


def get_app_root() -> Path:
    """Return the application root for source or PyInstaller (onedir) runs."""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parents[1]