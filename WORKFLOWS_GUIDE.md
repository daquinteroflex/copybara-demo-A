# Copybara GitHub Actions Workflows Guide

Complete guide to all automated workflows for syncing between copybara-demo-A and copybara-demo-B.

## Overview

This repository uses Copybara with GitHub Actions to maintain bidirectional sync between:
- **demo-A**: Source of truth with `private/` and `public/test_repo/` directories
- **demo-B**: Public mirror with only `public/test_repo/` contents at root level

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         demo-A (Private)                        │
│  ┌─────────────┐           ┌──────────────────────┐           │
│  │  private/   │           │  public/test_repo/   │           │
│  │ (internal)  │           │   (public code)      │           │
│  └─────────────┘           └──────────────────────┘           │
│                                      │                          │
│                                      │ A→B Sync                 │
│                                      ▼                          │
└──────────────────────────────────────────────────────────────────┘
                                       │
                    ┌──────────────────┼──────────────────┐
                    │                  │                  │
                    │        Bidirectional Sync           │
                    │                  │                  │
                    └──────────────────┼──────────────────┘
                                       │
┌──────────────────────────────────────────────────────────────────┐
│                         demo-B (Public)                          │
│                                                                   │
│              ┌───────────────────────────────┐                   │
│              │  Root directory               │                   │
│              │  (flattened public code)      │                   │
│              └───────────────────────────────┘                   │
│                            │                                      │
│                            │ B→A Sync + PR Import                 │
│                            ▼                                      │
└──────────────────────────────────────────────────────────────────┘
```

## Workflows

### 1. Initial Sync Workflow
**File:** `.github/workflows/copybara-initial-sync.yml`

**Purpose:** One-time baseline sync to establish history before continuous syncing.

**Triggers:**
- Manual only (`workflow_dispatch`)

**Options:**
- `mirror_to_public`: Sync B→A (recommended first)
- `public_to_mirror`: Sync A→B

**Usage:**
```bash
# Via GitHub UI: Actions → Copybara Initial Sync → Run workflow
# Select workflow type and run
```

**When to run:**
- First time setting up the sync
- After major repository restructuring
- To re-establish baseline after conflicts

---

### 2. A→B Continuous Sync
**File:** `.github/workflows/copybara-sync-a-to-b.yml`

**Purpose:** Automatically sync changes from demo-A's `public/test_repo/` to demo-B's root.

**Triggers:**
- Push to `main` branch in demo-A (only when `public/test_repo/**` changes)
- Schedule: Every 6 hours
- Manual trigger with optional dry-run

**What it does:**
1. Detects changes in demo-A's `public/test_repo/`
2. Transforms directory structure: `public/test_repo/` → root
3. Pushes directly to demo-B main branch
4. Preserves commit history

**Flow:**
```
demo-A/public/test_repo/src/file.py
           ↓
      Copybara
           ↓
    demo-B/src/file.py
```

**Manual trigger:**
```bash
# Via GitHub UI: Actions → Copybara Sync A→B → Run workflow
# Enable "dry_run" to preview changes
```

---

### 3. B→A Continuous Sync
**File:** `.github/workflows/copybara-sync-b-to-a.yml`

**Purpose:** Automatically sync changes from demo-B back to demo-A's `public/test_repo/`.

**Triggers:**
- Schedule: Every 30 minutes (polls demo-B for changes)
- Manual trigger with optional force sync
- Repository dispatch from demo-B (optional webhook)

**What it does:**
1. Checks demo-B for new commits
2. Compares with last synced commit (via `GitOrigin-RevId`)
3. If new commits found, syncs to demo-A
4. Transforms directory structure: root → `public/test_repo/`

**Smart sync:**
- Skips sync if no new commits detected
- Tracks sync state via commit metadata
- Force option to override skip logic

**Flow:**
```
demo-B/src/file.py
       ↓
   Copybara
       ↓
demo-A/public/test_repo/src/file.py
```

**Manual trigger:**
```bash
# Via GitHub UI: Actions → Copybara Sync B→A → Run workflow
# Enable "force" to sync even without new commits
# Enable "dry_run" to preview changes
```

---

### 4. PR Import from B→A
**File:** `.github/workflows/copybara-pr-sync.yml`

**Purpose:** Import PRs from demo-B as PRs in demo-A (not direct merge).

**Triggers:**
- Schedule: Every 30 minutes
- Manual trigger for specific PR or all open PRs

**What it does:**
1. Fetches open PRs from demo-B
2. For each PR:
   - Fetches baseline from demo-B main
   - Fetches parent from demo-A main
   - Creates new branch in demo-A: `copybara-import-${PR_NUMBER}`
   - Opens PR in demo-A with original metadata
3. Links back to original PR in demo-B

**PR Title Format:**
```
Import PR #123: Original PR Title
```

**PR Body Format:**
```markdown
This PR imports changes from demo-B PR #123

**Original PR:** https://github.com/.../pull/123
**Author:** @username

---
[Original PR body]
```

**Branch naming:**
```
copybara-import-2     # For demo-B PR #2
copybara-import-15    # For demo-B PR #15
```

**Manual trigger:**
```bash
# Import specific PR
# Via GitHub UI: Actions → Copybara PR Import → Run workflow
# Enter PR number: 5

# Import all open PRs
# Leave PR number blank
```

**Exit codes:**
- `0`: Success (PR imported)
- `4`: Skipped (no changes or already imported)
- Other: Failure

---

### 5. Optional: Webhook Trigger (demo-B)
**File:** `copybara-demo-B-webhook-trigger.yml` (place in demo-B repo)

**Purpose:** Trigger immediate B→A sync when demo-B main changes (instead of waiting 30 minutes).

**Setup:**
1. Use the same `COPYBARA_DEMO_TOKEN` secret in demo-B (no new token needed)
2. Token must have `workflow` scope for repository dispatch
3. Copy `copybara-demo-B-webhook-trigger.yml` to demo-B's `.github/workflows/trigger-sync.yml`

**What it does:**
- Sends repository dispatch event to demo-A
- Triggers B→A sync workflow immediately
- Reduces sync latency from 30 minutes to ~1 minute

**Benefits:**
- Real-time syncing for urgent changes
- Better developer experience
- Complements scheduled polling (fallback)

---

## Workflow Execution Flow

### Typical Development Flow

**Scenario 1: Change in demo-A**
```
1. Developer commits to demo-A/public/test_repo/
2. A→B sync triggers automatically (on push)
3. Changes appear in demo-B within minutes
4. No manual intervention needed
```

**Scenario 2: External Contribution via demo-B**
```
1. Contributor forks demo-B
2. Contributor opens PR in demo-B
3. PR import workflow detects new PR (every 30 min)
4. New PR created in demo-A with original metadata
5. Team reviews and merges PR in demo-A
6. A→B sync pushes merged changes back to demo-B
7. Original PR in demo-B gets updated/closed
```

**Scenario 3: Direct commit to demo-B**
```
1. Direct commit to demo-B main (rare, but possible)
2. B→A sync detects new commit (every 30 min)
3. Changes sync to demo-A/public/test_repo/
4. Team can review synced changes in demo-A
```

---

## Configuration

### Required Secrets

**Both demo-A and demo-B repositories:**
- `COPYBARA_DEMO_TOKEN`: Personal access token with:
  - `repo` scope (full control of both repositories)
  - `workflow` scope (for repository dispatch)
  - Access to both demo-A and demo-B

**Note:** The same token is used in both repositories for simplicity.

### Copybara Configuration

**File:** `copy.bara.sky`

**Workflows defined:**
1. `public_to_mirror` (A→B)
2. `mirror_to_public` (B→A)
3. `import_pr_from_b` (PR import)

**Key settings:**
```python
# A→B sync
origin_files = glob(["public/test_repo/**"])
transformations = [core.move("public/test_repo", "")]

# B→A sync
destination_files = glob(["public/test_repo/**"])
transformations = [core.move("", "public/test_repo")]

# PR import
destination = git.github_pr_destination(
    pr_branch = "copybara-import-${GITHUB_PR_NUMBER}",
    title = "Import PR #${GITHUB_PR_NUMBER}: ${GITHUB_PR_TITLE}",
)
```

---

## Monitoring & Troubleshooting

### Checking Sync Status

**Check recent A→B syncs:**
```bash
gh workflow view "Copybara Sync A→B (Continuous)" --repo daquinteroflex/copybara-demo-A
gh run list --workflow="Copybara Sync A→B (Continuous)" --repo daquinteroflex/copybara-demo-A
```

**Check recent B→A syncs:**
```bash
gh workflow view "Copybara Sync B→A (Continuous)" --repo daquinteroflex/copybara-demo-A
gh run list --workflow="Copybara Sync B→A (Continuous)" --repo daquinteroflex/copybara-demo-A
```

**Check PR imports:**
```bash
gh workflow view "Copybara PR Import from demo-B" --repo daquinteroflex/copybara-demo-A
gh run list --workflow="Copybara PR Import from demo-B" --repo daquinteroflex/copybara-demo-A
```

### Common Issues

**Issue: Sync skipped (exit code 4)**
- **Cause:** No new changes detected
- **Solution:** This is normal behavior, not an error
- **Force sync:** Use force option in manual trigger

**Issue: Merge conflicts**
- **Cause:** Conflicting changes in both repos
- **Solution:**
  1. Resolve conflicts manually in destination repo
  2. Push resolution
  3. Re-run sync workflow

**Issue: Authentication failed**
- **Cause:** Invalid or expired token
- **Solution:**
  1. Generate new personal access token
  2. Update `COPYBARA_DEMO_TOKEN` secret
  3. Verify token has required scopes

**Issue: PR import creates duplicate**
- **Cause:** PR already imported, state not tracked
- **Solution:**
  1. Close duplicate PR
  2. Check for existing import branch
  3. Original detection should prevent this

**Issue: B→A sync not detecting new commits**
- **Cause:** Missing `GitOrigin-RevId` in commit messages
- **Solution:**
  1. Run force sync once
  2. Future syncs should work correctly
  3. Verify `set_rev_id = True` in config

---

## Best Practices

### For Maintainers

1. **Always work in demo-A directly**
   - demo-A is the source of truth
   - Changes auto-sync to demo-B
   - Maintains private/ directory security

2. **Review PRs in demo-A, not demo-B**
   - Imported PRs provide context
   - Original PR links included
   - Easier to test with private/ code

3. **Monitor sync failures**
   - Set up notifications for failed runs
   - Check logs for authentication issues
   - Resolve conflicts promptly

4. **Use dry-run for testing**
   - Test sync changes before applying
   - Verify transformations work correctly
   - Preview merge conflicts

### For Contributors

1. **Fork demo-B, not demo-A**
   - demo-B is public mirror
   - Simpler structure (no private/)
   - PRs auto-import to demo-A

2. **Open PRs against demo-B main**
   - PRs will be imported to demo-A
   - Maintainers review in demo-A
   - Changes sync back to demo-B

3. **Wait for sync before testing**
   - After PR merge, wait ~5 minutes
   - Changes appear in demo-B automatically
   - No manual sync needed

---

## Workflow Matrix

| Workflow | Trigger | Frequency | Direction | Mode | Auto PR |
|----------|---------|-----------|-----------|------|---------|
| Initial Sync | Manual | One-time | Both | Direct push | No |
| A→B Sync | Push + Schedule | On change + 6hr | A→B | Direct push | No |
| B→A Sync | Schedule | 30 min | B→A | Direct push | No |
| PR Import | Schedule + Manual | 30 min | B→A | Creates PR | Yes |
| Webhook Trigger | Push (in demo-B) | On change | B→A | Triggers B→A | No |

---

## Advanced Configuration

### Adjusting Sync Frequency

**A→B sync (faster):**
```yaml
schedule:
  - cron: '0 */3 * * *'  # Every 3 hours
```

**B→A sync (more frequent):**
```yaml
schedule:
  - cron: '*/15 * * * *'  # Every 15 minutes
```

**PR import (less frequent):**
```yaml
schedule:
  - cron: '0 */2 * * *'  # Every 2 hours
```

### Adding File Filters

**Only sync specific file types:**
```python
# In copy.bara.sky
origin_files = glob([
    "public/test_repo/**/*.py",
    "public/test_repo/**/*.md",
])
```

### Custom PR Title/Body

**Modify PR import template:**
```python
# In copy.bara.sky
title = "[IMPORTED] ${GITHUB_PR_TITLE}",
body = "🤖 Auto-imported from demo-B\n\n" +
       "Original: ${GITHUB_PR_URL}\n" +
       "${GITHUB_PR_BODY}",
```

---

## Testing

### Test Initial Setup

1. Run initial sync (mirror_to_public)
2. Verify files appear in demo-A
3. Run initial sync (public_to_mirror)
4. Verify files appear in demo-B

### Test A→B Sync

1. Commit to demo-A `public/test_repo/`
2. Wait for workflow trigger (~1 min)
3. Check demo-B for changes
4. Verify commit history preserved

### Test B→A Sync

1. Commit to demo-B main
2. Wait for scheduled run (30 min) or force trigger
3. Check demo-A `public/test_repo/`
4. Verify changes synced

### Test PR Import

1. Open test PR in demo-B
2. Wait for scheduled run (30 min) or trigger manually
3. Check demo-A for imported PR
4. Verify metadata (title, body, author)
5. Merge PR in demo-A
6. Verify changes sync back to demo-B

---

## Maintenance

### Weekly Tasks
- Review failed workflow runs
- Check for pending PRs in both repos
- Verify sync frequency meets needs

### Monthly Tasks
- Review workflow logs for patterns
- Update tokens if expiring soon
- Check for Copybara updates

### As Needed
- Adjust sync schedules
- Add/remove file filters
- Update PR templates

---

## Getting Help

**Workflow fails:**
1. Check workflow logs in Actions tab
2. Look for error messages
3. Review common issues above
4. Check Copybara documentation

**Sync issues:**
1. Run dry-run to preview
2. Check for merge conflicts
3. Verify configuration in copy.bara.sky
4. Test with manual trigger

**Questions:**
- Check Copybara docs: https://github.com/google/copybara
- Review workflow YAML files
- Check GitHub Actions logs

---

## Summary

This setup provides:
- ✅ Automatic bidirectional sync
- ✅ PR import workflow
- ✅ Conflict detection
- ✅ Smart skip logic
- ✅ Manual override options
- ✅ Dry-run testing
- ✅ Comprehensive logging

All workflows run automatically with minimal manual intervention required.
