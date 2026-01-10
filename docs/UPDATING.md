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

⚠️ **Important:** GitHub templates create repos with **unrelated histories**. Use `cherry-pick` instead of `merge`.

### Method 1: Cherry-Pick (Recommended)

```bash
# Fetch latest changes
git fetch upstream

# See available updates
git log upstream/main --oneline | head -10

# Cherry-pick specific commits (e.g., the commit spam fix)
git cherry-pick d6a72fc
git cherry-pick ab6b64a

# If README.md conflicts (expected), keep your version:
git checkout --ours README.md
git add README.md
git cherry-pick --continue

# Push to your repository
git push origin main
```

### Method 2: Manual File Copy (Simple)

If cherry-pick is too complex, just copy specific files:

```bash
# Fetch latest changes
git fetch upstream

# Copy specific files from upstream
git checkout upstream/main -- .github/workflows/generate-terminal.yml
git checkout upstream/main -- scripts/generate_svg.py
git checkout upstream/main -- docs/UPDATING.md

# Commit
git commit -m "chore: Update from upstream template"
git push origin main
```

### Method 3: Merge (Only works if repos have shared history)

⚠️ This usually **doesn't work** for GitHub template repos:

```bash
git fetch upstream
git merge upstream/main  # Will likely fail with "unrelated histories"
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

Create `update.sh` for easy updates:

```bash
#!/bin/bash
# Fetch updates
git fetch upstream

# Show available updates
echo "=== Available Updates ==="
git log upstream/main --oneline | head -10
echo ""

# Ask which commits to cherry-pick
echo "Enter commit hashes to apply (space-separated):"
read -a commits

# Apply each commit
for commit in "${commits[@]}"; do
  echo "Applying $commit..."
  git cherry-pick "$commit"
  
  # Auto-resolve README conflicts
  if git status | grep -q "README.md"; then
    git checkout --ours README.md
    git add README.md
    git cherry-pick --continue
  fi
done

echo "Done! Push with: git push origin main"
```

Then just run: `./update.sh`

## Troubleshooting

### "Refusing to merge unrelated histories"

This is normal for GitHub template repos. Use **Method 1 (Cherry-Pick)** or **Method 2 (Manual Copy)** instead.

### README.md Conflicts

When cherry-picking, your README.md (your profile) will conflict with the template README:

```bash
# Always keep YOUR version:
git checkout --ours README.md
git add README.md
git cherry-pick --continue
```

### "Already exists" when cherry-picking

If you already have a commit, skip it:

```bash
git cherry-pick --skip
```

## Latest Updates

| Date | Update | Commit |
|------|--------|--------|
| 2026-01-10 | Fix: Workflow commit spam (amend instead of new commits) | `d6a72fc` |

---

**Tip:** Subscribe to the upstream repository ("Watch" → "Custom" → "Releases") to get notified of updates!
