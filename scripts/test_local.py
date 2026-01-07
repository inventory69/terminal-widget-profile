#!/usr/bin/env python3
"""
Local test script for Terminal Widget SVG Generator.

This script tests the SVG generation with mock data, without requiring
a GitHub API connection. Useful for development and visual testing.

Usage:
    python scripts/test_local.py [--theme THEME] [--open]

Options:
    --theme THEME   Theme to test (catppuccin, nord, gruvbox, tokyo_night)
    --open          Open the generated SVG in default browser
"""

import os
import sys
import argparse
import webbrowser
from pathlib import Path

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from jinja2 import Environment, FileSystemLoader
from snake_parser import prepare_embedded_snake, get_snake_dimensions


# Path to snake.svg in repository root
SNAKE_FILE = SCRIPT_DIR.parent / "snake.svg"


# Mock data for testing
MOCK_GITHUB_DATA = {
    "name": "Test User",
    "repositories": {
        "totalCount": 42,
        "nodes": [
            {
                "name": "awesome-project",
                "stargazerCount": 128,
                "description": "An awesome project that does cool things",
                "primaryLanguage": {"name": "Python", "color": "#3572A5"},
                "isFork": False
            },
            {
                "name": "terminal-widget-profile",
                "stargazerCount": 89,
                "description": "Terminal-style GitHub profile widget",
                "primaryLanguage": {"name": "Python", "color": "#3572A5"},
                "isFork": False
            },
            {
                "name": "cool-app",
                "stargazerCount": 45,
                "description": "A really cool application built with Rust",
                "primaryLanguage": {"name": "Rust", "color": "#dea584"},
                "isFork": False
            },
            {
                "name": "dotfiles",
                "stargazerCount": 23,
                "description": "My personal dotfiles for Arch Linux",
                "primaryLanguage": {"name": "Shell", "color": "#89e051"},
                "isFork": False
            },
            {
                "name": "web-project",
                "stargazerCount": 12,
                "description": "A modern web application",
                "primaryLanguage": {"name": "TypeScript", "color": "#3178c6"},
                "isFork": False
            }
        ]
    },
    "followers": {"totalCount": 256},
    "following": {"totalCount": 128}
}

MOCK_CONFIG = {
    "username": "testuser",
    "theme": "catppuccin",
    "bio": {
        "name": "Test User",
        "tagline": "Full-stack Developer • Open Source Enthusiast • Linux Fan",
        "website": "https://example.com",
        "links": [
            {"title": "LinkedIn", "url": "https://linkedin.com/in/testuser"},
            {"title": "Email", "url": "mailto:test@example.com"}
        ]
    },
    "display": {
        "show_bio": True,
        "show_stats": True,
        "show_projects": True,
        "show_snake": True,
        "max_projects": 4
    },
    "terminal": {
        "width": 800,
        "height": 680
    }
}


def process_repositories(repos, max_projects):
    """Process repository data and calculate total stars."""
    non_fork_repos = [r for r in repos if not r.get('isFork', False)]
    total_stars = sum(r.get('stargazerCount', 0) for r in non_fork_repos)
    
    formatted_projects = []
    for repo in non_fork_repos[:max_projects]:
        project = {
            'name': repo['name'],
            'stars': repo.get('stargazerCount', 0),
            'description': repo.get('description', 'No description') or 'No description',
            'language': repo.get('primaryLanguage', {}).get('name', 'Unknown') if repo.get('primaryLanguage') else 'Unknown',
        }
        if len(project['description']) > 50:
            project['description'] = project['description'][:47] + '...'
        formatted_projects.append(project)
    
    return total_stars, formatted_projects


def render_test_svg(config, github_data):
    """Render SVG from template with mock data."""
    repos = github_data['repositories']['nodes']
    total_stars, top_projects = process_repositories(
        repos,
        config['display']['max_projects']
    )
    
    # Prepare snake content if enabled and file exists
    snake_content = None
    snake_dims = {'width': 740, 'height': 160, 'scale': 0.84}
    
    if config['display'].get('show_snake', False) and SNAKE_FILE.exists():
        print("   🐍 Embedding snake animation...")
        snake_content = prepare_embedded_snake(
            SNAKE_FILE,
            theme=config['theme'],
            prefix='snk-',
            target_width=740.0
        )
        snake_dims = get_snake_dimensions(SNAKE_FILE, target_width=740.0)
        if snake_content:
            print(f"   Snake embedded ({len(snake_content)} chars)")
    
    template_data = {
        'username': config['username'],
        'display_name': github_data.get('name') or config['username'],
        'bio': config.get('bio', {}),
        'repos_count': github_data['repositories']['totalCount'],
        'total_stars': total_stars,
        'followers': github_data['followers']['totalCount'],
        'following': github_data['following']['totalCount'],
        'top_projects': top_projects,
        'display': config['display'],
        'terminal': config['terminal'],
        'theme': config['theme'],
        'snake_content': snake_content,
        'snake_dims': snake_dims,
    }
    
    templates_dir = SCRIPT_DIR / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('terminal.svg.j2')
    
    return template.render(**template_data)


def main():
    parser = argparse.ArgumentParser(description='Test Terminal Widget SVG generation locally')
    parser.add_argument('--theme', choices=['catppuccin', 'nord', 'gruvbox', 'tokyo_night'],
                        default='catppuccin', help='Theme to use')
    parser.add_argument('--open', action='store_true', help='Open SVG in browser')
    parser.add_argument('--all-themes', action='store_true', help='Generate all themes')
    args = parser.parse_args()
    
    print("🧪 Terminal Widget Local Test")
    print("=" * 40)
    
    themes = ['catppuccin', 'nord', 'gruvbox', 'tokyo_night'] if args.all_themes else [args.theme]
    
    for theme in themes:
        config = MOCK_CONFIG.copy()
        config['theme'] = theme
        
        print(f"\n📝 Generating with theme: {theme}")
        
        try:
            svg_content = render_test_svg(config, MOCK_GITHUB_DATA)
            
            # Output file
            output_file = Path(f"terminal-test-{theme}.svg")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            print(f"✅ Generated: {output_file}")
            print(f"   Size: {len(svg_content)} bytes")
            
            if args.open and theme == args.theme:
                print(f"🌐 Opening in browser...")
                webbrowser.open(f"file://{output_file.absolute()}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return 1
    
    print("\n" + "=" * 40)
    print("✅ Test complete!")
    print("\nTo view the SVG files:")
    print("  - Open terminal-test-*.svg in a browser")
    print("  - Or use: python scripts/test_local.py --open")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
