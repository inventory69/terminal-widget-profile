#!/usr/bin/env python3
"""
Terminal Widget SVG Generator for GitHub Profiles

This script generates an animated terminal-style SVG widget that displays:
- GitHub statistics (repos, stars, followers)
- Top projects (sorted by stars)
- Personal bio and links
- Contribution snake animation

The SVG is rendered from Jinja2 templates with customizable themes.
"""

import os
import sys
import requests
from jinja2 import Environment, FileSystemLoader, TemplateNotFound
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from snake_parser import prepare_embedded_snake, get_snake_dimensions


# Configuration
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "config.yaml"
TEMPLATES_DIR = SCRIPT_DIR / "templates"
# Output to repository root (parent of scripts directory)
OUTPUT_FILE = SCRIPT_DIR.parent / "terminal.svg"
SNAKE_FILE = SCRIPT_DIR.parent / "snake.svg"


def load_config() -> Dict[str, Any]:
    """Load configuration from config.yaml."""
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        # Validate required fields
        if not config.get('username'):
            raise ValueError("'username' is required in config.yaml")
            
        # Set defaults
        config.setdefault('theme', 'catppuccin')
        config.setdefault('display', {})
        config['display'].setdefault('show_bio', True)
        config['display'].setdefault('show_stats', True)
        config['display'].setdefault('show_projects', True)
        config['display'].setdefault('show_snake', True)
        config['display'].setdefault('max_projects', 4)
        config.setdefault('terminal', {})
        config['terminal'].setdefault('width', 800)
        config['terminal'].setdefault('height', 500)
        
        return config
        
    except FileNotFoundError:
        print(f"❌ Error: {CONFIG_FILE} not found!")
        sys.exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Error parsing {CONFIG_FILE}: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)


def fetch_github_data(username: str, token: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch user data from GitHub GraphQL API.
    
    Args:
        username: GitHub username
        token: GitHub personal access token (optional, increases rate limit)
        
    Returns:
        Dictionary containing user stats and repositories
    """
    headers = {
        "Content-Type": "application/json"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # GraphQL query to fetch user data
    query = """
    query($username: String!) {
      user(login: $username) {
        name
        repositories(first: 100, orderBy: {field: STARGAZERS, direction: DESC}, privacy: PUBLIC, ownerAffiliations: OWNER) {
          totalCount
          nodes {
            name
            stargazerCount
            description
            primaryLanguage {
              name
              color
            }
            isFork
          }
        }
        followers {
          totalCount
        }
        following {
          totalCount
        }
      }
    }
    """
    
    try:
        response = requests.post(
            "https://api.github.com/graphql",
            json={"query": query, "variables": {"username": username}},
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        
        data = response.json()
        
        if 'errors' in data:
            error_msg = data['errors'][0].get('message', 'Unknown error')
            print(f"❌ GitHub API error: {error_msg}")
            sys.exit(1)
            
        return data['data']['user']
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Error fetching GitHub data: {e}")
        sys.exit(1)


def process_repositories(repos: List[Dict], max_projects: int) -> tuple[int, List[Dict]]:
    """
    Process repository data and calculate total stars.
    
    Args:
        repos: List of repository dictionaries from GitHub API
        max_projects: Maximum number of projects to include
        
    Returns:
        Tuple of (total_stars, top_projects)
    """
    # Filter out forks and sort by stars
    non_fork_repos = [r for r in repos if not r.get('isFork', False)]
    
    # Calculate total stars
    total_stars = sum(r.get('stargazerCount', 0) for r in non_fork_repos)
    
    # Get top projects
    top_projects = non_fork_repos[:max_projects]
    
    # Format project data
    formatted_projects = []
    for repo in top_projects:
        project = {
            'name': repo['name'],
            'stars': repo.get('stargazerCount', 0),
            'description': repo.get('description', 'No description') or 'No description',
            'language': repo.get('primaryLanguage', {}).get('name', 'Unknown') if repo.get('primaryLanguage') else 'Unknown',
            'language_color': repo.get('primaryLanguage', {}).get('color', '#888888') if repo.get('primaryLanguage') else '#888888'
        }
        
        # Truncate description if too long
        if len(project['description']) > 50:
            project['description'] = project['description'][:47] + '...'
            
        formatted_projects.append(project)
    
    return total_stars, formatted_projects


def render_svg(config: Dict[str, Any], github_data: Dict[str, Any]) -> str:
    """
    Render SVG from Jinja2 template.
    
    Args:
        config: Configuration dictionary
        github_data: GitHub API data
        
    Returns:
        Rendered SVG as string
    """
    # Process repository data
    repos = github_data['repositories']['nodes']
    total_stars, top_projects = process_repositories(
        repos,
        config['display']['max_projects']
    )
    
    # Prepare snake content if enabled
    snake_content = None
    snake_dims = {'width': 740, 'height': 160, 'scale': 0.84}
    
    if config['display'].get('show_snake', False):
        if SNAKE_FILE.exists():
            print("🐍 Embedding snake animation...")
            snake_content = prepare_embedded_snake(
                SNAKE_FILE,
                theme=config['theme'],
                prefix='snk-',
                target_width=740.0
            )
            snake_dims = get_snake_dimensions(SNAKE_FILE, target_width=740.0)
            if snake_content:
                print(f"   Snake embedded ({len(snake_content)} chars)")
            else:
                print("   ⚠️  Failed to parse snake.svg")
        else:
            print(f"   ⚠️  snake.svg not found at {SNAKE_FILE}")
    
    # Prepare template data
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
    
    # Load Jinja2 environment
    try:
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        template = env.get_template('terminal.svg.j2')
        
        # Render SVG
        svg_content = template.render(**template_data)
        
        return svg_content
        
    except TemplateNotFound:
        print(f"❌ Error: Template 'terminal.svg.j2' not found in {TEMPLATES_DIR}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error rendering template: {e}")
        sys.exit(1)


def main():
    """Main execution function."""
    print("🚀 Generating terminal widget SVG...")
    
    # Load configuration
    print("📖 Loading configuration...")
    config = load_config()
    print(f"   Username: {config['username']}")
    print(f"   Theme: {config['theme']}")
    
    # Get GitHub token from environment
    github_token = os.getenv('GITHUB_TOKEN')
    if not github_token:
        print("⚠️  Warning: GITHUB_TOKEN not set (rate limit: 60/hour)")
    else:
        print("✅ Using GITHUB_TOKEN (rate limit: 5000/hour)")
    
    # Fetch GitHub data
    print("📊 Fetching GitHub data...")
    github_data = fetch_github_data(config['username'], github_token)
    print(f"   Repos: {github_data['repositories']['totalCount']}")
    print(f"   Followers: {github_data['followers']['totalCount']}")
    
    # Render SVG
    print("🎨 Rendering SVG template...")
    svg_content = render_svg(config, github_data)
    
    # Write to file
    print(f"💾 Writing to {OUTPUT_FILE}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(svg_content)
    
    print(f"✅ Successfully generated {OUTPUT_FILE}!")
    print(f"   Size: {len(svg_content)} bytes")
    print(f"\n📍 Embed in README.md:")
    print(f"   ![Terminal Widget](terminal.svg)")


if __name__ == "__main__":
    main()
