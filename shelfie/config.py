"""Where shelfie keeps its settings, and sensible defaults per platform."""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

APP = "shelfie"


def config_dir() -> Path:
    """Follow each platform's own convention rather than inventing one."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return Path(base) / APP
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / APP


CONFIG_PATH = config_dir() / "config.json"


def default_inboxes() -> List[str]:
    home = Path.home()
    out = [home / "Downloads", home / "Desktop"]
    return [str(p) for p in out if p.exists()]


def default_library() -> str:
    """Somewhere obvious, and not buried inside the user profile on Windows."""
    if sys.platform == "win32":
        drive = os.environ.get("SystemDrive", "C:")
        return str(Path(drive + "\\") / "Library")
    return str(Path.home() / "Library" if sys.platform == "darwin"
               else Path.home() / "library")


def blank() -> Dict[str, Any]:
    return {
        "version": 1,
        "library": default_library(),
        "inboxes": default_inboxes(),
        "strategy": "type",
        "min_age_days": 0,
        "keep_project_names": True,
        "make_vault": False,
        "vault_path": "",
    }


def load() -> Dict[str, Any]:
    try:
        with open(CONFIG_PATH, encoding="utf-8") as f:
            cfg = json.load(f)
        merged = blank()
        merged.update(cfg)
        return merged
    except (OSError, ValueError):
        return blank()


def save(cfg: Dict[str, Any]) -> Path:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return CONFIG_PATH


def exists() -> bool:
    return CONFIG_PATH.exists()


def projects(library: str) -> List[str]:
    """Existing project folders - the tool learns your clients from these."""
    p = Path(library) / "Projects"
    if not p.is_dir():
        return []
    try:
        return sorted([d.name for d in p.iterdir() if d.is_dir()])
    except OSError:
        return []
