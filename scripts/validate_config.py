#!/usr/bin/env python3
"""Validate scripts/config.yaml. Run as the first workflow step.

Exits 0 on success, 1 with a human-readable error on failure.
"""
from __future__ import annotations
import sys
from pathlib import Path
from typing import Any

import yaml

from themes import THEMES, ALIASES

CONFIG_FILE = Path(__file__).parent / "config.yaml"

VALID_LOGOS = {"arch", "cat", "none"}


def err(msg: str) -> None:
    print(f"❌ config.yaml: {msg}", file=sys.stderr)


def warn(msg: str) -> None:
    print(f"⚠️  config.yaml: {msg}")


def validate(cfg: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    if not isinstance(cfg, dict):
        return ["top-level must be a mapping"]

    username = cfg.get("username")
    if not username or not isinstance(username, str):
        errors.append("'username' is required and must be a non-empty string")
    elif username == "your-github-username":
        errors.append("'username' is still set to the placeholder — set your real GitHub username")

    theme = cfg.get("theme", "catppuccin")
    if theme not in THEMES and theme not in ALIASES:
        valid = ", ".join(sorted(set(THEMES) | set(ALIASES)))
        errors.append(f"'theme' = {theme!r} is unknown. Valid: {valid}")

    bio = cfg.get("bio")
    if bio is not None:
        if not isinstance(bio, dict):
            errors.append("'bio' must be a mapping")
        else:
            for k in ("name", "tagline", "website"):
                v = bio.get(k)
                if v is not None and not isinstance(v, str):
                    errors.append(f"'bio.{k}' must be a string")
            links = bio.get("links")
            if links is not None:
                if not isinstance(links, list):
                    errors.append("'bio.links' must be a list")
                else:
                    for i, link in enumerate(links):
                        if not isinstance(link, dict) or "title" not in link or "url" not in link:
                            errors.append(f"'bio.links[{i}]' must have 'title' and 'url'")

    fetch = cfg.get("fetch_fields")
    if fetch is not None and not isinstance(fetch, dict):
        errors.append("'fetch_fields' must be a mapping of name → value")

    display = cfg.get("display")
    if display is not None:
        if not isinstance(display, dict):
            errors.append("'display' must be a mapping")
        else:
            for k in ("show_bio", "show_fetch", "show_stats", "show_projects",
                     "show_palette", "embed_snake", "show_snake"):
                if k in display and not isinstance(display[k], bool):
                    errors.append(f"'display.{k}' must be true or false")
            mp = display.get("max_projects", 5)
            if not isinstance(mp, int) or not (1 <= mp <= 10):
                errors.append("'display.max_projects' must be an integer in [1, 10]")
            logo = display.get("ascii_logo", "arch")
            if logo not in VALID_LOGOS:
                errors.append(f"'display.ascii_logo' must be one of {sorted(VALID_LOGOS)}")

    return errors


def main() -> int:
    if not CONFIG_FILE.exists():
        err(f"file not found: {CONFIG_FILE}")
        return 1
    try:
        cfg = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        err(f"YAML parse error: {e}")
        return 1

    errors = validate(cfg or {})
    if errors:
        print("❌ Configuration is invalid:\n", file=sys.stderr)
        for e in errors:
            print(f"  • {e}", file=sys.stderr)
        print("\nSee scripts/config.yaml for the schema.", file=sys.stderr)
        return 1

    if cfg.get("theme") in ALIASES:
        warn(f"theme '{cfg['theme']}' is an alias for '{ALIASES[cfg['theme']]}'")
    if cfg.get("display", {}).get("show_snake") is not None:
        warn("'display.show_snake' is deprecated, use 'display.embed_snake'")

    print("✅ config.yaml is valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
