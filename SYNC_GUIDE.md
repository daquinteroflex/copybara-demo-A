# Copybara Sync Guide

This guide provides step-by-step instructions for running Copybara workflows to sync between copybara-demo-A and copybara-demo-B.

## Prerequisites

### Install Copybara

**Option 1: Pre-built Release (Recommended)**
```bash
# Download latest release from GitHub
# https://github.com/google/copybara/releases
wget https://github.com/google/copybara/releases/download/SNAPSHOT/copybara
chmod +x copybara
mv copybara /usr/local/bin/
```

**Option 2: Docker**
```bash
# Use Copybara Docker image
docker pull ghcr.io/google/copybara:latest
```

**Verify Installation**
```bash
copybara --version
# or with Docker:
docker run ghcr.io/google/copybara:latest --version
```

### Authentication Setup

Copybara needs access to both GitHub repositories:

```bash
# Set up SSH keys for GitHub (if not already done)
ssh-keygen -t ed25519 -C "your_email@example.com"
cat ~/.ssh/id_ed25519.pub  # Add this to GitHub Settings → SSH Keys

# Or use GitHub token
export GITHUB_TOKEN="your_github_personal_access_token"
```

## Running Workflows

### Workflow 1: A → B (Public to Mirror)

Syncs changes from demo-A's `public/test_repo/` to demo-B's root.

**Initial Sync (First Time Only)**
```bash
# Run from copybara-demo-A directory
copybara copy.bara.sky public_to_mirror --init-history

# With Docker:
docker run -v "$(pwd)":/usr/src/app -w /usr/src/app \
  -v ~/.ssh:/root/.ssh \
  ghcr.io/google/copybara:latest \
  copy.bara.sky public_to_mirror --init-history
```

**Regular Sync**
```bash
# After initial sync, use regular mode
copybara copy.bara.sky public_to_mirror

# Dry run to preview changes without committing:
copybara copy.bara.sky public_to_mirror --dry-run
```

### Workflow 2: B → A (Mirror to Public)

Syncs contributions from demo-B back to demo-A's `public/test_repo/`.

**Initial Sync (First Time Only)**
```bash
copybara copy.bara.sky mirror_to_public --init-history
```

**Regular Sync**
```bash
copybara copy.bara.sky mirror_to_public

# Dry run to preview:
copybara copy.bara.sky mirror_to_public --dry-run
```

## Testing End-to-End Sync

### Test 1: A → B Sync

1. **Make a change in demo-A**
   ```bash
   cd public/test_repo/src/demo_package
   # Edit core.py to add a new function
   ```

2. **Commit the change**
   ```bash
   git add .
   git commit -m "Add new feature to core.py"
   git push origin main
   ```

3. **Run Copybara A→B workflow**
   ```bash
   cd /path/to/copybara-demo-A
   copybara copy.bara.sky public_to_mirror
   ```

4. **Verify in demo-B**
   ```bash
   cd /path/to/copybara-demo-B
   git pull origin main
   # Check that src/demo_package/core.py has your changes
   ```

### Test 2: B → A Sync

1. **Make a change in demo-B**
   ```bash
   cd /path/to/copybara-demo-B
   # Edit tests/test_core.py to add a new test
   git add .
   git commit -m "Add new test case"
   git push origin main
   ```

2. **Run Copybara B→A workflow**
   ```bash
   cd /path/to/copybara-demo-A
   copybara copy.bara.sky mirror_to_public
   ```

3. **Verify in demo-A**
   ```bash
   git pull origin main
   # Check that public/test_repo/tests/test_core.py has your changes
   ```

### Test 3: Verify Private File Isolation

1. **Check demo-B doesn't have private files**
   ```bash
   cd /path/to/copybara-demo-B
   ls -la
   # Should NOT see private/ directory or any files from it
   ```

2. **Verify private files remain in demo-A**
   ```bash
   cd /path/to/copybara-demo-A
   ls -la private/
   # Should see internal_config.py and private_utils.py
   ```

## Common Commands

### Dry Run (Preview Only)
```bash
# Preview A→B sync without making changes
copybara copy.bara.sky public_to_mirror --dry-run

# Preview B→A sync without making changes
copybara copy.bara.sky mirror_to_public --dry-run
```

### Validate Configuration
```bash
# Check if copy.bara.sky is valid
copybara copy.bara.sky --validate
```

### Force Sync (Use with Caution)
```bash
# Force overwrite destination (careful!)
copybara copy.bara.sky public_to_mirror --force
```

## Troubleshooting

### Error: "No new changes to import"
- This means both repos are already in sync
- No action needed

### Error: "Merge conflict detected"
- Demo-A is the source of truth
- Manually resolve conflicts in demo-A
- Re-run the workflow

### Error: "Authentication failed"
- Check SSH keys: `ssh -T git@github.com`
- Or verify GitHub token is set: `echo $GITHUB_TOKEN`

### Error: "Cannot find origin ref"
- Ensure both repos have a `main` branch
- Check branch names in copy.bara.sky match actual branches

## Best Practices

1. **Always dry-run first**: Use `--dry-run` to preview changes
2. **Sync regularly**: Avoid large divergences between repos
3. **Demo-A is authoritative**: Resolve conflicts in demo-A
4. **Test both directions**: After setup, test A→B and B→A
5. **Monitor sync**: Check GitHub commits after each Copybara run

## Automation (Optional)

For continuous sync, set up GitHub Actions:

```yaml
# .github/workflows/copybara-sync.yml
name: Copybara Sync
on:
  push:
    branches: [main]
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: olivr/copybara-action@v1
        with:
          ssh_key: ${{ secrets.SSH_KEY }}
          command: copy.bara.sky public_to_mirror
```

## Next Steps

After validating this trial setup:
1. Document lessons learned
2. Identify any issues or limitations
3. Apply configuration to production repositories
4. Set up automated syncing if desired
