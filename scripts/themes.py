"""
Centralized theme palettes with semantic color roles.

Each theme defines:
  base     — main background
  surface  — cards / inset sections
  overlay  — borders, dividers
  muted    — dimmed text (paths, descriptions)
  text     — primary foreground
  accent   — highlighted labels (user, branch, headings)
  green    — success / contributions / shell prompt
  yellow   — stars
  red      — accent 2 / errors
  purple   — accent 3
  colors   — 8-color terminal palette (used by the bottom palette bar)
"""

from __future__ import annotations
from typing import Dict, Any

# fmt: off
THEMES: Dict[str, Dict[str, Any]] = {
    "catppuccin": {  # Mocha
        "base": "#1e1e2e", "surface": "#181825", "overlay": "#313244",
        "muted": "#7f849c", "text": "#cdd6f4", "accent": "#89b4fa",
        "green": "#a6e3a1", "yellow": "#f9e2af", "red": "#f38ba8", "purple": "#cba6f7",
        "colors": ["#45475a", "#f38ba8", "#a6e3a1", "#f9e2af", "#89b4fa", "#cba6f7", "#94e2d5", "#bac2de"],
    },
    "nord": {
        "base": "#2e3440", "surface": "#3b4252", "overlay": "#434c5e",
        "muted": "#7b88a1", "text": "#e5e9f0", "accent": "#88c0d0",
        "green": "#a3be8c", "yellow": "#ebcb8b", "red": "#bf616a", "purple": "#b48ead",
        "colors": ["#3b4252", "#bf616a", "#a3be8c", "#ebcb8b", "#81a1c1", "#b48ead", "#88c0d0", "#e5e9f0"],
    },
    "gruvbox": {  # Dark, medium contrast
        "base": "#282828", "surface": "#1d2021", "overlay": "#3c3836",
        "muted": "#928374", "text": "#ebdbb2", "accent": "#83a598",
        "green": "#b8bb26", "yellow": "#fabd2f", "red": "#fb4934", "purple": "#d3869b",
        "colors": ["#3c3836", "#fb4934", "#b8bb26", "#fabd2f", "#83a598", "#d3869b", "#8ec07c", "#ebdbb2"],
    },
    "tokyo_night_storm": {
        "base": "#24283b", "surface": "#1f2335", "overlay": "#3b4261",
        "muted": "#787c99", "text": "#c0caf5", "accent": "#7aa2f7",
        "green": "#9ece6a", "yellow": "#e0af68", "red": "#f7768e", "purple": "#bb9af7",
        "colors": ["#414868", "#f7768e", "#9ece6a", "#e0af68", "#7aa2f7", "#bb9af7", "#7dcfff", "#c0caf5"],
    },
    "rose_pine": {
        "base": "#191724", "surface": "#1f1d2e", "overlay": "#26233a",
        "muted": "#6e6a86", "text": "#e0def4", "accent": "#c4a7e7",
        "green": "#9ccfd8", "yellow": "#f6c177", "red": "#eb6f92", "purple": "#c4a7e7",
        "colors": ["#26233a", "#eb6f92", "#31748f", "#f6c177", "#9ccfd8", "#c4a7e7", "#ebbcba", "#e0def4"],
    },
    "everforest": {  # Dark, medium
        "base": "#2d353b", "surface": "#272e33", "overlay": "#3d484d",
        "muted": "#859289", "text": "#d3c6aa", "accent": "#7fbbb3",
        "green": "#a7c080", "yellow": "#dbbc7f", "red": "#e67e80", "purple": "#d699b6",
        "colors": ["#3d484d", "#e67e80", "#a7c080", "#dbbc7f", "#7fbbb3", "#d699b6", "#83c092", "#d3c6aa"],
    },
}
# fmt: on

ALIASES: Dict[str, str] = {
    "tokyo_night": "tokyo_night_storm",
}


def resolve(name: str) -> Dict[str, Any]:
    """Resolve a theme name (with alias support) to a palette dict.

    Raises KeyError with a helpful message if unknown.
    """
    key = ALIASES.get(name, name)
    if key not in THEMES:
        available = ", ".join(sorted(set(THEMES) | set(ALIASES)))
        raise KeyError(
            f"Unknown theme '{name}'. Available: {available}"
        )
    return THEMES[key]


def all_names() -> list[str]:
    """Return all canonical theme names (without aliases)."""
    return sorted(THEMES.keys())
