# Configuration Guide

All settings are in `scripts/config.yaml`.

## Required Settings

```yaml
username: your-github-username  # Your GitHub username
```

## Theme

```yaml
theme: catppuccin  # catppuccin | nord | gruvbox | tokyo_night
```

| Theme | Colors | Style |
|-------|--------|-------|
| **catppuccin** | Purple/Blue on dark | Modern, soft |
| **nord** | Cyan/White on blue-gray | Minimal, Scandinavian |
| **gruvbox** | Green/Beige on dark | Retro, warm |
| **tokyo_night** | Neon blue on dark | Futuristic |

## Personal Bio

```yaml
bio:
  name: "Your Display Name"      # Optional, defaults to GitHub name
  tagline: "Your role • Interests"
  website: "https://yoursite.com"
  links:
    - title: "LinkedIn"
      url: "https://linkedin.com/in/you"
    - title: "Email"
      url: "mailto:you@example.com"
```

## Display Options

```yaml
display:
  show_bio: true        # Show bio section
  show_stats: true      # Show GitHub stats
  show_projects: true   # Show top projects
  show_snake: true      # Contribution activity grid
  max_projects: 4       # 1-10 projects
```

**Note:** Only your own repositories are shown (no forks or contributed repos).

## Widget Size

```yaml
terminal:
  width: 800   # Pixels
  height: 500  # Pixels (auto-adjusts)
```

## Examples

### Minimal (stats only)

```yaml
display:
  show_bio: false
  show_stats: true
  show_projects: false
  show_snake: false
```

### Projects showcase

```yaml
display:
  show_bio: true
  show_stats: false
  show_projects: true
  max_projects: 6
```
