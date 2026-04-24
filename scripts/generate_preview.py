#!/usr/bin/env python3
"""Generate preview SVGs for all themes using mock GitHub data.

Use for local iteration and to produce README screenshots.
No network access, no GITHUB_TOKEN required.

Usage:
  python scripts/generate_preview.py                # all themes
  python scripts/generate_preview.py catppuccin     # one theme
  python scripts/generate_preview.py --out docs/img # custom output dir
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

import themes
import generate_svg as gen

ROOT = Path(__file__).parent.parent
DEFAULT_OUT = ROOT / "docs" / "previews"

MOCK_GH = {
    "name": "Jane Ricer",
    "followers": {"totalCount": 137},
    "following": {"totalCount": 42},
    "repositories": {
        "totalCount": 38,
        "nodes": [
            {"name": "hyprland-dots",      "stargazerCount": 1284, "isFork": False,
             "primaryLanguage": {"name": "Lua",        "color": "#000080"}},
            {"name": "neofetch-themes",    "stargazerCount": 412,  "isFork": False,
             "primaryLanguage": {"name": "Shell",      "color": "#89e051"}},
            {"name": "waybar-modules",     "stargazerCount": 198,  "isFork": False,
             "primaryLanguage": {"name": "C++",        "color": "#f34b7d"}},
            {"name": "rofi-launchers",     "stargazerCount": 87,   "isFork": False,
             "primaryLanguage": {"name": "Rasi",       "color": "#a3be8c"}},
            {"name": "terminal-widget",    "stargazerCount": 56,   "isFork": False,
             "primaryLanguage": {"name": "Python",     "color": "#3572A5"}},
        ],
    },
}

MOCK_CONFIG = {
    "username": "jane-ricer",
    "theme": "catppuccin",
    "bio": {
        "name": "Jane Ricer",
        "tagline": "Arch enjoyer • Hyprland tinkerer • OSS",
        "website": "https://jane.dev",
        "links": [
            {"title": "GitHub",   "url": "https://github.com/jane-ricer"},
            {"title": "Mastodon", "url": "https://fosstodon.org/@jane"},
        ],
    },
    "fetch_fields": {
        "os":       "Arch Linux",
        "wm":       "Hyprland",
        "shell":    "fish",
        "terminal": "Kitty",
        "editor":   "Neovim",
    },
    "display": {
        "show_bio": True, "show_fetch": True, "show_stats": True,
        "show_projects": True, "show_palette": True,
        "ascii_logo": "arch", "embed_snake": False, "max_projects": 5,
    },
}


def render_one(theme: str, out_dir: Path) -> Path:
    import copy
    cfg = copy.deepcopy(MOCK_CONFIG)
    cfg["theme"] = theme
    svg = gen.render(cfg, MOCK_GH)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"preview-{theme}.svg"
    out_file.write_text(svg, encoding="utf-8")
    print(f"  ✓ {out_file.resolve().relative_to(ROOT)} ({len(svg.encode('utf-8'))} bytes)")
    return out_file


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("theme", nargs="?", help="single theme; default = all")
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    targets = [args.theme] if args.theme else themes.all_names()
    for t in targets:
        if t not in themes.THEMES and t not in themes.ALIASES:
            sys.exit(f"❌ unknown theme: {t}")
    print(f"🎨 rendering {len(targets)} preview(s) → {args.out}")
    for t in targets:
        render_one(t, args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
