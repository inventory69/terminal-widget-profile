# Updating from Upstream

If you used this repository as a template for your profile, you can pull updates from the original repository.

## One-Time Setup: Add Upstream Remote

```bash
cd YOUR_USERNAME  # Your profile repository

# Add the original repository as "upstream"
git remote add upstream https://github.com/inventory69/terminal-widget-profile.git

# Verify
git remote -v
# origin    https://github.com/YOUR_USERNAME/YOUR_USERNAME.git (fetch)
# upstream  https://github.com/inventory69/terminal-widget-profile.git (fetch)
```

## Get Updates

```bash
# Fetch latest changes from upstream
git fetch upstream

# Merge upstream changes into your main branch
git checkout main
git merge upstream/main

# If there are conflicts, resolve them, then:
git add .
git commit -m "chore: Merge upstream updates"

# Push to your repository
git push origin main
```

## What Gets Updated?

- ✅ **Workflow fixes** (like the commit spam fix)
- ✅ **New features** in `generate_svg.py`
- ✅ **New themes** in `scripts/templates/`
- ✅ **Bug fixes**

## What Stays Yours?

Your personal configuration is safe:
- ⚠️ `scripts/config.yaml` - **May conflict** (keep your changes)
- ✅ `README.md` - Your profile README
- ✅ Generated SVGs (`terminal.svg`, `snake.svg`)

## Handling Conflicts

If `config.yaml` has conflicts:

```bash
# Keep your version
git checkout --ours scripts/config.yaml
git add scripts/config.yaml
git commit -m "chore: Keep personal config"

# Or manually edit the file to merge changes
```

## Quick Update Script

Create `update.sh`:

```bash
#!/bin/bash
git fetch upstream
git merge upstream/main
git push origin main
```

Then just run: `./update.sh`

## Alternative: Cherry-Pick Specific Fixes

If you only want specific updates (e.g., the commit spam fix):

```bash
# Find the commit hash on upstream
git fetch upstream
git log upstream/main --oneline | head -20

# Cherry-pick specific commit
git cherry-pick <commit-hash>
git push origin main
```

Example for the commit spam fix:

```bash
git fetch upstream
git cherry-pick d6a72fc  # The commit spam fix
git push origin main
```

## Latest Updates

| Date | Update | Commit |
|------|--------|--------|
| 2026-01-10 | Fix: Workflow commit spam (amend instead of new commits) | `d6a72fc` |

---

**Tip:** Subscribe to the upstream repository ("Watch" → "Custom" → "Releases") to get notified of updates!
