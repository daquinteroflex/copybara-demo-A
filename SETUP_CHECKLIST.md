# Copybara Workflows Setup Checklist

Quick checklist to get all workflows running.

## Prerequisites

- [ ] Two GitHub repositories: demo-A (private) and demo-B (public)
- [ ] Personal access token with `repo` and `workflow` scopes
- [ ] Copybara configuration file (`copy.bara.sky`) in demo-A

## Step 1: Add Secrets

### In demo-A repository:
1. Go to Settings → Secrets and variables → Actions
2. Create new secret: `COPYBARA_DEMO_TOKEN`
3. Paste your personal access token

### In demo-B repository (optional, for webhook):
1. Go to Settings → Secrets and variables → Actions
2. Create new secret: `COPYBARA_DEMO_TOKEN`
3. Paste the **same** personal access token

## Step 2: Deploy Workflows to demo-A

Copy these workflow files to `.github/workflows/` in demo-A:

- [ ] `copybara-initial-sync.yml` ✅ (already exists)
- [ ] `copybara-pr-sync.yml` ✅ (already exists)
- [ ] `copybara-sync-a-to-b.yml` ✅ (new)
- [ ] `copybara-sync-b-to-a.yml` ✅ (new)

Commit and push to main branch.

## Step 3: Run Initial Sync

1. Go to Actions tab in demo-A
2. Select "Copybara Initial Sync" workflow
3. Click "Run workflow"
4. Choose `mirror_to_public` (B→A first)
5. Wait for completion
6. Run again with `public_to_mirror` (A→B)

**Result:** Both repositories should now have matching content.

## Step 4: Verify Workflows

### Check A→B Sync:
1. Edit a file in `demo-A/public/test_repo/`
2. Commit and push to main
3. Go to Actions → Check "Copybara Sync A→B" runs
4. Verify changes appear in demo-B within 5 minutes

### Check B→A Sync:
1. Edit a file in demo-B (via GitHub UI or local)
2. Commit to main
3. Wait up to 30 minutes (or trigger manually)
4. Check "Copybara Sync B→A" in Actions
5. Verify changes appear in `demo-A/public/test_repo/`

### Check PR Import:
1. Create a test PR in demo-B
2. Wait up to 30 minutes (or trigger manually)
3. Check "Copybara PR Import" in Actions
4. Verify PR created in demo-A with prefix "Import PR #..."
5. Check PR has original metadata and link

## Step 5: Optional - Setup Webhook (Instant B→A sync)

1. Copy `copybara-demo-B-webhook-trigger.yml`
2. Place in demo-B at `.github/workflows/trigger-sync.yml`
3. Commit and push

**Result:** B→A syncs trigger immediately on push (instead of waiting 30 min).

## Workflow Status

| Workflow | Status | Trigger | Frequency |
|----------|--------|---------|-----------|
| Initial Sync | Manual only | One-time | As needed |
| A→B Sync | ⏰ Auto | Push + 6hr | Continuous |
| B→A Sync | ⏰ Auto | 30min poll | Continuous |
| PR Import | ⏰ Auto | 30min poll | Continuous |
| Webhook (opt) | ⏰ Auto | Push in B | Instant |

## Troubleshooting

### Workflow not appearing in Actions tab
- Workflow files must be in `main` branch
- File must be in `.github/workflows/` directory
- YAML syntax must be valid

### Workflow failing with authentication error
- Check `COPYBARA_DEMO_TOKEN` secret exists
- Verify token has `repo` and `workflow` scopes
- Token must have access to both repositories

### Sync showing "no changes" (exit code 4)
- This is normal when repositories are in sync
- Not an error, just informational
- Use force option to override if needed

### PR import not creating PR
- Check copybara config uses `git.github_pr_destination`
- Verify PR is OPEN in demo-B
- Check workflow logs for errors
- Try dry-run first to test

## Verification Commands

```bash
# List workflows in demo-A
gh workflow list --repo daquinteroflex/copybara-demo-A

# Check A→B sync runs
gh run list --workflow="Copybara Sync A→B" --limit 5 --repo daquinteroflex/copybara-demo-A

# Check B→A sync runs
gh run list --workflow="Copybara Sync B→A" --limit 5 --repo daquinteroflex/copybara-demo-A

# Check PR imports
gh run list --workflow="Copybara PR Import" --limit 5 --repo daquinteroflex/copybara-demo-A

# Trigger manual sync
gh workflow run "Copybara Sync A→B" --repo daquinteroflex/copybara-demo-A

# Trigger with dry-run
gh workflow run "Copybara Sync B→A" --repo daquinteroflex/copybara-demo-A \
  -f dry_run=true
```

## Next Steps

After setup complete:

1. **Test the full flow:**
   - Make change in demo-A → See in demo-B
   - Open PR in demo-B → See imported to demo-A
   - Merge in demo-A → See back in demo-B

2. **Adjust schedules if needed:**
   - Edit cron expressions in workflow files
   - More frequent: `*/15 * * * *` (15 min)
   - Less frequent: `0 */12 * * *` (12 hours)

3. **Monitor for first week:**
   - Check Actions tab daily
   - Verify syncs working
   - Watch for failures

4. **Set up notifications:**
   - Go to demo-A → Settings → Notifications
   - Enable email for workflow failures
   - Or use Slack/Discord webhooks

## Success Criteria

✅ All workflows appear in Actions tab
✅ Initial sync completed successfully
✅ A→B sync triggers on push
✅ B→A sync runs every 30 minutes
✅ PR import creates PRs in demo-A
✅ Changes flow bidirectionally
✅ No authentication errors

## Quick Reference

**Force sync B→A:**
```bash
gh workflow run "Copybara Sync B→A (Continuous)" \
  --repo daquinteroflex/copybara-demo-A \
  -f force=true
```

**Import specific PR:**
```bash
gh workflow run "Copybara PR Import from demo-B" \
  --repo daquinteroflex/copybara-demo-A \
  -f pr_number=5
```

**Dry run A→B:**
```bash
gh workflow run "Copybara Sync A→B (Continuous)" \
  --repo daquinteroflex/copybara-demo-A \
  -f dry_run=true
```

---

**All set!** Your bidirectional Copybara sync is now fully automated. 🎉
