# Terminal Widget Profile

A terminal-style SVG widget for your GitHub profile. Auto-updates via GitHub Actions.

<div align="center">
  <img src="terminal.svg" alt="Terminal Widget Preview" width="700"/>
</div>

## Quick Start

1. **Use this template** → Create repo as `<your-username>/<your-username>`
2. **Edit** `scripts/config.yaml`:
   ```yaml
   username: YOUR_GITHUB_USERNAME
   theme: catppuccin  # catppuccin | nord | gruvbox | tokyo_night
   ```
3. **Enable Actions** → Run "Generate Terminal Widget" workflow
4. **Done!** Widget appears at `terminal.svg`

## Features

| Feature | Description |
|---------|-------------|
| 📊 **Live Stats** | Repos, stars, followers (updates every 6h) |
| 🚀 **Top Projects** | Your best repos, sorted by stars |
| 👤 **Personal Bio** | Name, tagline, website, links |
| 🎨 **4 Themes** | Catppuccin, Nord, Gruvbox, Tokyo Night |
| ⚡ **Lightweight** | Pure SVG, ~7KB |

## Configuration

Edit [`scripts/config.yaml`](scripts/config.yaml):

```yaml
username: your-username
theme: catppuccin

bio:
  name: "Your Name"
  tagline: "Developer • Open Source"
  website: "https://yoursite.com"
  links:
    - title: "LinkedIn"
      url: "https://linkedin.com/in/you"

display:
  show_bio: true
  show_stats: true
  show_projects: true
  max_projects: 4
```

## Themes

| Catppuccin | Nord | Gruvbox | Tokyo Night |
|------------|------|---------|-------------|
| `#1e1e2e` | `#2e3440` | `#282828` | `#1a1b26` |

## Docs

- [Configuration Guide](docs/CONFIGURATION.md)
- [Development & Testing](docs/DEVELOPMENT.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## License

MIT
