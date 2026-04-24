#!/usr/bin/env python3
"""Generate the terminal widget SVG.

Pipeline:
  config.yaml  →  GitHub GraphQL  →  themes/logos  →  widget.svg.j2  →  terminal.svg
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Optional

import requests
import yaml
from jinja2 import Environment, FileSystemLoader

import themes
import logos
from snake_parser import prepare_embedded_snake, get_snake_dimensions

SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent
CONFIG_FILE = SCRIPT_DIR / "config.yaml"
TEMPLATES_DIR = SCRIPT_DIR / "templates"
OUTPUT_FILE = ROOT / "terminal.svg"
SNAKE_FILE = ROOT / "snake.svg"

# Nerd-Font glyphs by fetch_field key (lowercase).
# Falls back to a generic dot if the key is unknown.
# Glyphs use universally-available Unicode (works in DejaVu/Noto/system fonts
# that GitHub renders SVGs with). Nerd Font codepoints would render as empty
# boxes for most viewers, so we use geometric shapes that look terminal-y.
GLYPHS = {
    "os":       ("◆", "accent"),
    "kernel":   ("◇", "muted"),
    "wm":       ("▣", "purple"),
    "de":       ("▣", "purple"),
    "shell":    ("❯", "green"),
    "terminal": ("▶", "accent"),
    "editor":   ("✎", "yellow"),
    "host":     ("❖", "muted"),
    "cpu":      ("■", "red"),
    "gpu":      ("▤", "purple"),
    "memory":   ("▰", "yellow"),
    "uptime":   ("○", "green"),
    "packages": ("⦿", "accent"),
}
DEFAULT_GLYPH = ("•", "accent")

DEFAULT_FETCH = {
    "os": "Arch Linux",
    "wm": "Hyprland",
    "shell": "bash",
    "terminal": "Kitty",
    "editor": "Neovim",
}


def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        sys.exit(f"❌ Missing {CONFIG_FILE}")
    cfg = yaml.safe_load(CONFIG_FILE.read_text(encoding="utf-8")) or {}
    if not cfg.get("username"):
        sys.exit("❌ 'username' is required in config.yaml")

    cfg.setdefault("theme", "catppuccin")
    cfg.setdefault("bio", {})
    cfg.setdefault("fetch_fields", DEFAULT_FETCH.copy())

    d = cfg.setdefault("display", {})
    d.setdefault("show_bio", True)
    d.setdefault("show_fetch", True)
    d.setdefault("show_stats", True)
    d.setdefault("show_projects", True)
    d.setdefault("show_palette", True)
    d.setdefault("ascii_logo", "arch")
    d.setdefault("max_projects", 5)
    # Backwards compat: old `show_snake` → `embed_snake`
    if "embed_snake" not in d:
        d["embed_snake"] = bool(d.get("show_snake", False))

    return cfg


def fetch_github(username: str, token: Optional[str]) -> dict[str, Any]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    query = """
    query($username: String!) {
      user(login: $username) {
        name
        followers { totalCount }
        following { totalCount }
        repositories(first: 100, orderBy: {field: STARGAZERS, direction: DESC},
                     privacy: PUBLIC, ownerAffiliations: OWNER) {
          totalCount
          nodes {
            name stargazerCount isFork
            primaryLanguage { name color }
          }
        }
      }
    }
    """
    r = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": {"username": username}},
        headers=headers, timeout=15,
    )
    r.raise_for_status()
    data = r.json()
    if "errors" in data:
        sys.exit(f"❌ GitHub API error: {data['errors'][0].get('message')}")
    return data["data"]["user"]


def project_rows(repos: list[dict], limit: int) -> tuple[int, list[dict]]:
    own = [r for r in repos if not r.get("isFork")]
    total_stars = sum(r.get("stargazerCount", 0) for r in own)
    out = []
    for r in own[:limit]:
        lang = r.get("primaryLanguage") or {}
        out.append({
            "name": r["name"][:28],
            "stars": r.get("stargazerCount", 0),
            "language": lang.get("name", "—"),
            "language_color": lang.get("color") or "#888",
        })
    return total_stars, out


def fetch_rows(fields: dict[str, str]) -> list[tuple[str, str, str, str]]:
    rows = []
    for key, value in fields.items():
        glyph, color = GLYPHS.get(key.lower(), DEFAULT_GLYPH)
        label = key.upper() if len(key) <= 3 else key.capitalize()
        rows.append((glyph, label, str(value), color))
    return rows


def compute_height(cfg: dict, theme: dict, fetch_count: int, project_count: int,
                   has_logo: bool, snake_h: int) -> int:
    h = 50  # title bar + top padding
    d = cfg["display"]
    bio = cfg.get("bio") or {}

    # Header
    bio_h = 0
    if d["show_bio"] and bio:
        bio_h = 50
        if bio.get("tagline"): bio_h += 18
        if bio.get("website"): bio_h += 16
        if bio.get("links"):   bio_h += 16
    logo_h = (len(logos.get(d["ascii_logo"])) * 13 + 4) if has_logo else 0
    h += max(bio_h, logo_h, 50) + 14

    if d["show_fetch"] and fetch_count:
        h += fetch_count * 18 + 24 + 12
    if d["show_projects"] and project_count:
        h += project_count * 22 + 22 + 12
    if d["show_stats"]:
        h += 20
    if d["embed_snake"] and snake_h:
        h += snake_h + 12
    if d["show_palette"]:
        h += 28
    h += 28  # prompt
    return h


def render(cfg: dict, gh: dict) -> str:
    theme = themes.resolve(cfg["theme"])
    repos = gh["repositories"]["nodes"]
    total_stars, projects = project_rows(repos, cfg["display"]["max_projects"])
    rows = fetch_rows(cfg["fetch_fields"]) if cfg["display"]["show_fetch"] else []

    logo = logos.get(cfg["display"]["ascii_logo"])
    has_logo = bool(logo)

    snake_content = None
    snake_dims = {"width": 0, "height": 0, "scale": 1}
    if cfg["display"]["embed_snake"] and SNAKE_FILE.exists():
        snake_content = prepare_embedded_snake(
            SNAKE_FILE, theme=cfg["theme"], prefix="snk-", target_width=700.0,
        )
        snake_dims = get_snake_dimensions(SNAKE_FILE, target_width=700.0)

    W = 740
    H = compute_height(cfg, theme, len(rows), len(projects),
                       has_logo, int(snake_dims.get("height", 0)))

    env = Environment(loader=FileSystemLoader(TEMPLATES_DIR),
                      trim_blocks=True, lstrip_blocks=True)
    tpl = env.get_template("widget.svg.j2")
    return tpl.render(
        W=W, H=H, t=theme,
        username=cfg["username"],
        display_name=gh.get("name") or cfg["username"],
        bio=cfg.get("bio") or {},
        display=cfg["display"],
        fetch_rows=rows,
        top_projects=projects,
        repos_count=gh["repositories"]["totalCount"],
        total_stars=total_stars,
        followers=gh["followers"]["totalCount"],
        following=gh["following"]["totalCount"],
        logo=logo,
        snake_content=snake_content,
        snake_dims=snake_dims,
    )


def update_readme_links(cfg: dict) -> None:
    """Regenerate the <!-- WIDGET-LINKS-START/END --> block in README.md from config."""
    readme = ROOT / "README.md"
    if not readme.exists():
        return

    bio = cfg.get("bio") or {}
    website = bio.get("website", "")
    links = bio.get("links") or []

    # Primary href for the SVG image wrapper
    img_href = website or (links[0]["url"] if links else "#")

    # Build individual link elements
    link_parts = []
    if website:
        display = website.replace("https://", "").replace("http://", "").rstrip("/")
        link_parts.append(f'<a href="{website}">↗ {display}</a>')
    for link in links:
        url = link["url"]
        title = link["title"]
        icon = "✉" if url.startswith("mailto:") else "↗"
        link_parts.append(f'<a href="{url}">{icon} {title}</a>')

    separator = "\n  &nbsp;·&nbsp;\n  "
    links_line = separator.join(link_parts) if link_parts else ""

    inner = (
        f'<div align="center">\n'
        f'  <a href="{img_href}">\n'
        f'    <img src="terminal.svg" alt="Terminal Widget" width="800"/>\n'
        f'  </a>\n'
    )
    if links_line:
        inner += f'  <br/>\n  {links_line}\n'
    inner += "</div>"

    START = "<!-- WIDGET-LINKS-START -->"
    END = "<!-- WIDGET-LINKS-END -->"
    new_block = f"{START}\n{inner}\n{END}"

    content = readme.read_text(encoding="utf-8")
    if START in content and END in content:
        s = content.index(START)
        e = content.index(END) + len(END)
        content = content[:s] + new_block + content[e:]
        readme.write_text(content, encoding="utf-8")
        print("📝 updated README.md widget links")
    else:
        print("⚠️  README.md: WIDGET-LINKS markers not found, skipping link update")


def main() -> int:
    cfg = load_config()
    print(f"📖 user={cfg['username']} theme={cfg['theme']}")
    token = os.getenv("GITHUB_TOKEN")
    print("✅ token present" if token else "⚠️  no GITHUB_TOKEN (60/h limit)")
    gh = fetch_github(cfg["username"], token)
    svg = render(cfg, gh)
    OUTPUT_FILE.write_text(svg, encoding="utf-8")
    print(f"💾 wrote {OUTPUT_FILE} ({len(svg.encode('utf-8'))} bytes)")
    update_readme_links(cfg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
