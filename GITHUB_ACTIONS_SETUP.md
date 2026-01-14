# GitHub Actions Setup for Automated PR Import

This guide explains how to set up automated PR import from copybara-demo-B to copybara-demo-A using GitHub Actions.

## Workflow File Created

**Location:** `.github/workflows/copybara-pr-sync.yml`

This workflow automatically imports PRs from demo-B to demo-A using Copybara.

---

## How to Set Up

### Step 1: Create the .github/workflows directory

```bash
cd /path/to/copybara-demo-A
mkdir -p .github/workflows
```

### Step 2: Copy the workflow file

```bash
# Copy from the template
cp .github/workflows/copybara-pr-sync.yml .github/workflows/

# Or create it manually by copying the content
```

### Step 3: Configure GitHub Token (if needed)

The workflow uses `${{ secrets.GITHUB_TOKEN }}` which is automatically provided by GitHub Actions.

**For cross-repository access**, you may need a Personal Access Token (PAT):

1. Go to GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token with these scopes:
   - ✅ `repo` (Full control of private repositories)
   - ✅ `workflow` (Update GitHub Action workflows)
3. Copy the token
4. In demo-A repo: Settings → Secrets and variables → Actions → New repository secret
5. Name: `COPYBARA_TOKEN`
6. Value: Paste your token

Then update the workflow to use the PAT:
```yaml
token: ${{ secrets.COPYBARA_TOKEN }}
```

### Step 4: Commit and Push

```bash
git add .github/workflows/copybara-pr-sync.yml
git commit -m "Add Copybara PR import workflow"
git push origin main
```

---

## How to Use

### Trigger Method 1: Manual Run (Specific PR)

1. Go to **Actions** tab in demo-A repo
2. Select **"Copybara PR Import from demo-B"** workflow
3. Click **"Run workflow"**
4. Fill in inputs:
   - **pr_number**: Enter the PR number from demo-B (e.g., `5`)
   - **dry_run**: Check for preview, uncheck to run for real

**Example:**
- PR #5 exists in demo-B
- Enter `5` in pr_number
- Click "Run workflow"
- Copybara will import PR #5 from demo-B to demo-A

### Trigger Method 2: Manual Run (All PRs)

1. Go to **Actions** tab in demo-A repo
2. Select **"Copybara PR Import from demo-B"** workflow
3. Click **"Run workflow"**
4. Leave **pr_number** empty
5. Copybara will import ALL open PRs from demo-B

### Trigger Method 3: Automatic (Schedule)

The workflow runs automatically **every 30 minutes** to check for new PRs.

To change the schedule, edit the cron expression:
```yaml
schedule:
  - cron: '*/30 * * * *'  # Every 30 minutes
  # - cron: '0 * * * *'   # Every hour
  # - cron: '0 */6 * * *' # Every 6 hours
```

### Trigger Method 4: On Push (Testing)

For testing, you can trigger by pushing to a specific branch:
```bash
git checkout -b copybara-pr-sync-test
git push origin copybara-pr-sync-test
```

---

## Workflow Behavior

### What It Does

1. **Checks out demo-A** with sparse checkout (only needed files)
2. **Configures Git** with Copybara Bot identity
3. **Runs Copybara** with `import_pr_from_b` workflow
4. **Creates a PR** in demo-A with the imported changes
5. **Generates a summary** of the import

### What Gets Imported

- **Source:** Any OPEN PR from `copybara-demo-B`
- **Destination:** `copybara-demo-A/public/test_repo/`
- **Transformation:** Demo-B root → Demo-A `public/test_repo/`

### Requirements for Import

Based on your current configuration:
- ✅ PR must be **OPEN**
- ❌ **No labels required** (removed)
- ❌ **No approvals required** (removed)
- ✅ **No status checks required** (optional)

---

## Workflow Inputs

| Input | Description | Required | Default |
|-------|-------------|----------|---------|
| `pr_number` | Specific PR number to import from demo-B | No | (empty = all PRs) |
| `dry_run` | Preview only, no changes | No | `false` |

---

## Example Scenarios

### Scenario 1: Import a Specific PR

**Situation:** PR #7 was created in demo-B, you want to import it immediately.

**Steps:**
1. Go to Actions → "Copybara PR Import from demo-B"
2. Run workflow
3. Enter `7` for pr_number
4. Check "dry_run" for preview first
5. Click "Run workflow"
6. Review the dry run output
7. Run again without dry_run to import

**Result:** PR #7 from demo-B is imported to demo-A as a new PR.

### Scenario 2: Batch Import All PRs

**Situation:** Multiple PRs were created in demo-B over the weekend.

**Steps:**
1. Go to Actions → "Copybara PR Import from demo-B"
2. Run workflow
3. Leave pr_number empty
4. Click "Run workflow"

**Result:** All open PRs from demo-B are imported to demo-A.

### Scenario 3: Automatic Import

**Situation:** You want PRs to automatically import every 30 minutes.

**Steps:**
1. No action needed - workflow runs on schedule
2. Check Actions tab to see automatic runs
3. Review PRs created in demo-A

**Result:** Every 30 minutes, the workflow checks for new PRs and imports them.

---

## Monitoring and Debugging

### View Workflow Runs

1. Go to **Actions** tab in demo-A
2. Select a workflow run
3. Click on the job to see logs

### Check Summary

Each run creates a summary with:
- Mode (dry run or live)
- Source PR information
- Destination directory
- Checklist of what to verify

### Common Issues

#### Error: "PR does not exist"

**Cause:** PR number doesn't exist in demo-B

**Solution:** Verify PR exists with:
```bash
gh pr list --repo daquinteroflex/copybara-demo-B
```

#### Error: "Authentication failed"

**Cause:** GitHub token doesn't have access to demo-B

**Solution:**
1. Create a PAT with `repo` scope
2. Add it as `COPYBARA_TOKEN` secret
3. Update workflow to use the PAT

#### Error: "No changes to import"

**Cause:** PR already imported or no new commits

**Solution:** This is normal - no action needed

#### Error: "Merge conflict"

**Cause:** PR conflicts with existing code in demo-A

**Solution:**
1. Manually resolve conflict in demo-A
2. Re-run import

### Debug Mode

To get more verbose output, the workflow already includes `--verbose` flag:
```yaml
--verbose
```

For even more detail, you can add:
```yaml
--verbose --debug
```

---

## Customization

### Change Schedule

Edit the cron expression:
```yaml
schedule:
  - cron: '0 9 * * *'  # Daily at 9 AM UTC
```

### Change Branch Naming

Edit the PR branch name:
```yaml
--github-destination-pr-branch="custom-prefix/import-pr-${PR_NUMBER}-$(date +%Y%m%d)"
```

### Add Notifications

Add a notification step (e.g., Slack):
```yaml
- name: Notify Slack
  if: success()
  uses: slackapi/slack-github-action@v1
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK }}
    payload: |
      {
        "text": "✅ Copybara imported PR #${{ inputs.pr_number }}"
      }
```

### Add Filters

To add label requirements at runtime, modify the copybara command:
```yaml
--github-required-label=ready-for-import \
```

---

## Testing the Workflow

### Test 1: Dry Run

1. Create a test PR in demo-B
2. Run workflow with dry_run=true
3. Check logs for what would be imported
4. No actual changes made

### Test 2: Import Test PR

1. Run workflow with specific PR number
2. Check demo-A for new PR
3. Verify changes are in `public/test_repo/`
4. Close/delete test PR if not needed

### Test 3: Scheduled Run

1. Wait for scheduled run (or push to test branch)
2. Check Actions tab for automatic run
3. Verify PRs were imported

---

## Security Considerations

### Token Permissions

The workflow requires:
- ✅ `contents: write` - To push changes
- ✅ `pull-requests: write` - To create PRs

### Sparse Checkout

The workflow only checks out necessary files:
```yaml
sparse-checkout: |
  copy.bara.sky
  public/test_repo
  .gitignore
```

This reduces attack surface and speeds up checkout.

### Private Files

The configuration ensures private/ directory is never synced:
```python
destination_files = glob(["public/test_repo/**"])
```

### Review PRs

**Important:** Always review imported PRs before merging:
- ✅ No secrets leaked
- ✅ Changes are appropriate
- ✅ Tests pass
- ✅ No malicious code

---

## Maintenance

### Update Copybara Version

The workflow uses `ghcr.io/anipos/copybara-docker-image`.

To use a specific version:
```yaml
container:
  image: ghcr.io/anipos/copybara-docker-image:v1.2.3
```

### Update Schedule

Adjust based on PR frequency:
- High activity: Every 15-30 minutes
- Medium activity: Every 1-2 hours
- Low activity: Daily

### Disable Automatic Import

Comment out the schedule trigger:
```yaml
# schedule:
#   - cron: '*/30 * * * *'
```

---

## Next Steps

1. ✅ Create `.github/workflows/` directory
2. ✅ Add workflow file
3. ✅ Configure tokens if needed
4. ✅ Commit and push
5. ✅ Test with dry run
6. ✅ Test with real PR import
7. ✅ Monitor scheduled runs
8. ✅ Document for team

---

## Support

For issues:
1. Check workflow logs in Actions tab
2. Verify copy.bara.sky configuration
3. Test manually with copybara CLI
4. Review Copybara documentation: https://github.com/google/copybara
