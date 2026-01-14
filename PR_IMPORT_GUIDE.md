# PR Import and Event-Driven Workflows Guide

This guide explains the new PR import and event-driven feedback workflows added to `copy.bara.sky`.

## What Was Added

### 1. **Workflow 3: `import_pr_from_b`** (PR Import)
- **Purpose**: Automatically import approved PRs from demo-B to demo-A
- **Type**: EVENT-DRIVEN using `git.github_pr_origin`
- **Mode**: CHANGE_REQUEST (creates individual commits for each PR)

### 2. **Workflow 4: `pr_feedback`** (Automated Feedback)
- **Purpose**: Respond to GitHub events with automated actions
- **Type**: TRIGGER-BASED using `git.github_trigger`
- **Actions**: Add labels, post comments, update status checks

---

## How to Use

### Manual PR Import

**Import a specific PR:**
```bash
cd /path/to/copybara-demo-A

# Import PR #5 from demo-B to demo-A
copybara copy.bara.sky import_pr_from_b --github-pr-number=5

# Dry run first (recommended)
copybara copy.bara.sky import_pr_from_b --github-pr-number=5 --dry-run
```

**Requirements for PR to be imported:**
- ✓ PR must be **OPEN**
- ✓ PR must have **`copybara:import`** label
- ✓ PR must be **approved** by COLLABORATOR/MEMBER/OWNER
- ✓ Review state: `HEAD_COMMIT_APPROVED`
- ✓ Optional status checks must pass (if configured)

### Batch Mode (Check All PRs)

```bash
# Import ALL ready PRs from demo-B
copybara copy.bara.sky import_pr_from_b

# This will check all open PRs and import any that meet criteria
```

### Run Feedback Workflow

```bash
# Monitor and respond to GitHub events
copybara copy.bara.sky pr_feedback
```

---

## Configuration Details

### PR Import Criteria

The `import_pr_from_b` workflow uses these filters:

```python
required_labels = ["copybara:import"]         # Must have this label
review_state = "HEAD_COMMIT_APPROVED"         # Must be approved
review_approvers = ["COLLABORATOR", "MEMBER", "OWNER"]
state = "OPEN"                                # Must be open
```

### Optional Filters (Currently Commented Out)

You can uncomment these in `copy.bara.sky` to add more requirements:

```python
# Require specific CI checks
required_status_context_names = ["CI/test", "CI/build"]

# Require specific check runs
required_check_runs = ["unit-tests", "linter"]

# Only import PRs targeting specific branch
branch = "main"
```

### Event Triggers

The `pr_feedback` workflow subscribes to these GitHub events:

- `PULL_REQUEST` - PR opened, closed, updated, etc.
- `PULL_REQUEST_REVIEW_COMMENT` - Comments on PR code
- `STATUS` - Status checks updated
- `CHECK_RUNS` - GitHub Actions check runs completed

---

## Command Line Flags

Override configuration via CLI:

```bash
# Override required labels
copybara copy.bara.sky import_pr_from_b \
  --github-required-label=ready-for-import

# Add required status checks
copybara copy.bara.sky import_pr_from_b \
  --github-required-status-context-name=CI/test \
  --github-required-status-context-name=CI/build

# Add required check runs
copybara copy.bara.sky import_pr_from_b \
  --github-required-check-run=unit-tests
```

---

## Testing the Setup

### Step 1: Create a Test PR in demo-B

```bash
cd /path/to/copybara-demo-B

# Make a change
echo "# Test PR" >> test_file.txt
git checkout -b test-pr
git add test_file.txt
git commit -m "Test PR for copybara import"
git push origin test-pr

# Create PR on GitHub
gh pr create --title "Test: Copybara Import" --body "Testing PR import workflow"
```

### Step 2: Add Required Label

```bash
# Add the import label to the PR
gh pr edit <PR_NUMBER> --add-label "copybara:import"

# Or via GitHub UI:
# - Go to the PR
# - Add label: copybara:import
```

### Step 3: Get Approval

- Have a COLLABORATOR/MEMBER/OWNER approve the PR
- Or if you have permissions, approve it yourself

### Step 4: Run Import (Dry Run First)

```bash
cd /path/to/copybara-demo-A

# Preview the import
copybara copy.bara.sky import_pr_from_b \
  --github-pr-number=<PR_NUMBER> \
  --dry-run

# If looks good, run for real
copybara copy.bara.sky import_pr_from_b \
  --github-pr-number=<PR_NUMBER>
```

### Step 5: Verify Import

```bash
# Check demo-A for the changes
cd /path/to/copybara-demo-A
git pull origin main

# Changes should appear in public/test_repo/
ls -la public/test_repo/

# Check commit message for PR metadata
git log -1
# Should show: "Imported-From-PR: <PR_NUMBER>"
```

---

## Automation Options

### Option A: GitHub Actions (Recommended)

Create `.github/workflows/copybara-import.yml` in demo-A:

```yaml
name: Copybara PR Import
on:
  schedule:
    - cron: '*/30 * * * *'  # Every 30 minutes
  workflow_dispatch:

jobs:
  import:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Download Copybara
        run: |
          wget https://github.com/google/copybara/releases/latest/download/copybara_deploy.jar
      - name: Import Ready PRs
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          java -jar copybara_deploy.jar copy.bara.sky import_pr_from_b
```

### Option B: Cron Job

```bash
# Add to crontab
crontab -e

# Run every 15 minutes
*/15 * * * * cd /path/to/copybara-demo-A && copybara copy.bara.sky import_pr_from_b >> /var/log/copybara.log 2>&1
```

### Option C: Webhook Service

For real-time event-driven imports, create a webhook service:

1. **Create webhook endpoint**
   - Listen for GitHub webhook POST requests
   - Parse PR events

2. **Trigger Copybara**
   - When PR is labeled/approved, run:
   - `copybara copy.bara.sky import_pr_from_b --github-pr-number=<PR>`

3. **Example webhook handler** (pseudocode):
```python
@app.post("/webhook")
def handle_webhook(request):
    event = request.json
    if event['action'] == 'labeled' and 'copybara:import' in event['labels']:
        pr_number = event['pull_request']['number']
        subprocess.run([
            'copybara', 'copy.bara.sky', 'import_pr_from_b',
            f'--github-pr-number={pr_number}'
        ])
```

---

## Troubleshooting

### Error: "PR does not meet requirements"

**Cause**: PR missing label, approval, or status checks

**Solution**:
```bash
# Check PR status
gh pr view <PR_NUMBER>

# Add label if missing
gh pr edit <PR_NUMBER> --add-label "copybara:import"

# Get approval if needed
# (must be done by COLLABORATOR/MEMBER/OWNER)
```

### Error: "No changes to import"

**Cause**: PR already imported or no new commits

**Solution**: This is normal if PR is already synced

### Error: "Authentication failed"

**Cause**: Missing GitHub credentials

**Solution**:
```bash
# Set up GitHub token
export GITHUB_TOKEN="your_personal_access_token"

# Or configure SSH
ssh-keygen -t ed25519
# Add public key to GitHub
```

### Error: "Cannot find PR"

**Cause**: PR number doesn't exist or is in different repo

**Solution**:
```bash
# Verify PR exists in demo-B
gh pr list --repo daquinteroflex/copybara-demo-B

# Use correct PR number
```

---

## Best Practices

1. **Always dry-run first**
   ```bash
   copybara copy.bara.sky import_pr_from_b --github-pr-number=5 --dry-run
   ```

2. **Use labels for control**
   - Only add `copybara:import` when ready
   - Remove label to prevent re-import

3. **Require approvals**
   - Don't import unapproved PRs
   - Use review_state requirements

4. **Add status checks** (optional but recommended)
   - Uncomment `required_status_context_names`
   - Ensure CI passes before import

5. **Monitor regularly**
   - Set up scheduled checks (every 15-30 min)
   - Check logs for errors

6. **Document for contributors**
   - Add PR template in demo-B
   - Explain the `copybara:import` label
   - List approval requirements

---

## Next Steps

1. **Validate configuration**:
   ```bash
   copybara copy.bara.sky --validate
   ```

2. **Test with a real PR**:
   - Create test PR in demo-B
   - Add label and approval
   - Run import workflow

3. **Set up automation**:
   - Choose GitHub Actions, cron, or webhook
   - Test automated runs

4. **Customize as needed**:
   - Add more required labels
   - Configure status checks
   - Add custom transformations

5. **Document for team**:
   - Update demo-B README
   - Add PR template with instructions
   - Share import process with contributors
