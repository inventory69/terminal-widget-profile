# Troubleshooting

## Widget not updating

1. Check **Actions** tab for failed runs
2. Hard refresh browser: `Ctrl+Shift+R`
3. GitHub caches images ~10 minutes

## Theme not applied

1. Check theme name: `catppuccin`, `nord`, `gruvbox`, `tokyo_night`
2. Verify CSS file exists in `scripts/templates/`
3. Re-run workflow manually

## Rate limit exceeded

Create a Personal Access Token:

1. https://github.com/settings/tokens
2. Generate token with `public_repo` scope
3. Add as secret: Repo → Settings → Secrets → `GH_TOKEN`

## SVG shows errors

Run local test:

```bash
python scripts/test_local.py --theme catppuccin
```

Check for Python errors in output.

## Actions not running

1. Actions tab → Enable workflows
2. Check workflow file syntax
3. Verify permissions: `contents: write`
