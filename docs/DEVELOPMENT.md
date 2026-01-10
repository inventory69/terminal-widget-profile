# Development & Testing

## Local Testing (No API needed)

Test with mock data:

```bash
pip install -r requirements.txt

# Test all themes
python scripts/test_local.py --all-themes

# Test specific theme
python scripts/test_local.py --theme nord

# Open in browser
python scripts/test_local.py --open
```

Generates `terminal-test-*.svg` files.

## Testing with Real Data

```bash
export GITHUB_TOKEN=ghp_your_token
python scripts/generate_svg.py
```

## Project Structure

```
.
├── .github/workflows/
│   └── generate-terminal.yml  # Runs every 6 hours
├── scripts/
│   ├── generate_svg.py        # Main generator
│   ├── test_local.py          # Local testing
│   ├── config.yaml            # Configuration
│   └── templates/
│       ├── terminal.svg.j2    # SVG template
│       └── *.css.j2           # Theme styles
├── terminal.svg               # Generated output
└── docs/                      # Documentation
```

## How It Works

```
GitHub Actions (cron: every 6h)
    ↓
Fetch GitHub GraphQL API
    ↓
Render Jinja2 template
    ↓
Commit terminal.svg
    ↓
Profile displays updated widget
```

## GitHub API

Uses GraphQL for:
- Repository count & stars
- Follower count
- Top repositories (by stars)

**Rate limits:**
- Without token: 60/hour
- With token: 5,000/hour

GitHub Actions provides `GITHUB_TOKEN` automatically.
