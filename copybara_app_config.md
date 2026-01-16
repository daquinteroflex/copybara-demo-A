# GitHub App Configuration for Copybara Actions

This guide explains how to set up and use the Copybara GitHub App credentials to enable automated workflows.

## 1. Setup Instructions (Internal App)

To use the code proposed in our workflow, we must use an **Internal GitHub App** that we own. We cannot use a 3rd-party App because we lack the Private Key.

### Step 1: Register the App
1. Go to **Organization Settings** > **Developer settings** > **GitHub Apps** > **New GitHub App**.
2. **Name:** `Copybara-Sync-Bot` (or similar).
3. **Homepage:** Your repository URL.
4. **Webhooks:** Uncheck "Active" (unless specifically needed).
5. **Permissions:** - **Contents:** Read & Write
   - **Pull requests:** Read & Write
   - **Metadata:** Read-only (automatic)
6. Click **Create GitHub App**.

### Step 2: Generate the Private Key
1. Scroll down to the **Private keys** section on the App's general settings page.
2. Click **Generate a private key**.
3. A `.pem` file will download. **Keep this file secure.**

### Step 3: Install the App
1. In the left sidebar, click **Install App**.
2. Click **Install** next to your organization and select the relevant repositories.

---

## 2. Storing Secrets in GitHub

Add these values to your repository under **Settings > Secrets and variables > Actions**:

| Name | Type | Value Source |
| :--- | :--- | :--- |
| `COPYBARA_APP_ID` | **Variable** | Found in the "About" section of your App settings. |
| `COPYBARA_PRIVATE_KEY` | **Secret** | The entire text content of the downloaded `.pem` file. |

---

## 3. Workflow Implementation

Copy and paste this into your `.github/workflows/` file.

```yaml
jobs:
  copybara-job:
    runs-on: ubuntu-latest
    steps:
      # This step exchanges the App ID and Private Key for a temporary Token
      - name: Generate Token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ vars.COPYBARA_APP_ID }}
          private-key: ${{ secrets.COPYBARA_APP_PRIVATE_KEY }}

      # Use the generated token for downstream steps
      - name: Run Staging Tests
        uses: ./actions/staging-tests
        with:
          token: ${{ steps.app-token.outputs.token }}
