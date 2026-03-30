"""
rubui.config
~~~~~~~~~~~~
Configuration loading with priority: CLI > local rubui.toml > global config > defaults.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

# Python 3.11+ has tomllib; older versions need the tomli backport.
try:
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:
    try:
        import tomli as tomllib  # type: ignore[import-not-found,no-redef]
    except ModuleNotFoundError:
        tomllib = None  # type: ignore[assignment]


# ── paths ──────────────────────────────────────────────────────────────────

LOCAL_CONFIG = Path("rubui.toml")


def _global_config_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    return base / "rubui"


def global_config_path() -> Path:
    return _global_config_dir() / "rubui.toml"


# ── dataclass ──────────────────────────────────────────────────────────────


@dataclass
class AppConfig:
    """Merged configuration for rubui."""

    mode: str = "manual"
    theme: str = "dark"
    scramble_on_start: bool = False
    solve_on_start: bool = False
    color: bool = True
    fps: int = 60
    speed: float = 0.05
    scramble_length: int = 25
    scramble_seed: Optional[int] = None
    size: Optional[int] = None

    def merge_toml(self, data: dict[str, Any]) -> None:
        """Overlay a parsed TOML dict onto this config (lower priority)."""
        app = data.get("app", {})
        auto = data.get("auto", {})
        scr = data.get("scramble", {})

        if "mode" in app and self.mode == "manual":
            self.mode = app["mode"]
        if "theme" in app and self.theme == "dark":
            self.theme = app["theme"]
        if "scramble_on_start" in app:
            self.scramble_on_start = self.scramble_on_start or app["scramble_on_start"]
        if "solve_on_start" in app:
            self.solve_on_start = self.solve_on_start or app["solve_on_start"]
        if "color" in app:
            self.color = self.color and app["color"]
        if "size" in app:
            self.size = app["size"]
        if "fps" in auto and self.fps == 60:
            self.fps = auto["fps"]
        if "speed" in auto and self.speed == 0.05:
            self.speed = auto["speed"]
        if "length" in scr and self.scramble_length == 25:
            self.scramble_length = scr["length"]
        if "seed" in scr and self.scramble_seed is None:
            seed_val = scr["seed"]
            self.scramble_seed = seed_val if seed_val != 0 else None


# ── loading ────────────────────────────────────────────────────────────────


def _load_toml(path: Path) -> dict[str, Any] | None:
    if tomllib is None:
        return None
    if not path.is_file():
        return None
    try:
        with open(path, "rb") as fh:
            return tomllib.load(fh)
    except Exception:
        return None


def load_config(
    *,
    cli_mode: str | None = None,
    cli_theme: str | None = None,
    cli_scramble: bool = False,
    cli_solve: bool = False,
    cli_speed: float | None = None,
    cli_fps: int | None = None,
    cli_seed: int | None = None,
    cli_no_color: bool = False,
    cli_size: int | None = None,
) -> AppConfig:
    """Build the final merged ``AppConfig``."""

    cfg = AppConfig()

    # Layer 3: global config (lowest file priority)
    global_data = _load_toml(global_config_path())
    if global_data:
        cfg.merge_toml(global_data)

    # Layer 2: local config
    local_data = _load_toml(LOCAL_CONFIG)
    if local_data:
        cfg.merge_toml(local_data)

    # Layer 1: CLI overrides (highest priority)
    if cli_mode is not None:
        cfg.mode = cli_mode
    if cli_theme is not None:
        cfg.theme = cli_theme
    if cli_scramble:
        cfg.scramble_on_start = True
    if cli_solve:
        cfg.solve_on_start = True
    if cli_speed is not None:
        cfg.speed = cli_speed
    if cli_fps is not None:
        cfg.fps = cli_fps
    if cli_seed is not None:
        cfg.scramble_seed = cli_seed
    if cli_no_color:
        cfg.color = False
    if cli_size is not None:
        cfg.size = cli_size

    return cfg


# ── init command helper ───────────────────────────────────────────────────

DEFAULT_CONFIG_CONTENT = """\
# rubui configuration
# See: https://github.com/programmersd21/rubui

[app]
mode = "manual"
theme = "dark"
scramble_on_start = false
solve_on_start = false
color = true

[auto]
fps = 60
speed = 0.05

[scramble]
length = 25
seed = 0
"""


def generate_default_config(force: bool = False) -> tuple[Path, bool]:
    """Create the global default config file.

    Returns (path, created).
    """
    path = global_config_path()
    if path.exists() and not force:
        return path, False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(DEFAULT_CONFIG_CONTENT, encoding="utf-8")
    return path, True
