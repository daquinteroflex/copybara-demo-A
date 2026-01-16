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

### Which Pattern Should I Use?

- **Option A (Single Job)**: Use when running on standard GitHub-hosted runners
- **Option B (Two Jobs)**: Use when you need to run commands inside a Docker container (e.g., Copybara container)

**Why two jobs for containers?**
The `actions/create-github-app-token@v2` action doesn't work properly inside custom Docker containers. By generating the token in a separate job and passing it as an output, we can use the token inside the container job.

### Option A: Single Job (Standard Runner)

Use this pattern when running on standard GitHub runners without custom containers:

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
          private-key: ${{ secrets.COPYBARA_PRIVATE_KEY }}

      # Use the generated token for downstream steps
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          token: ${{ steps.app-token.outputs.token }}

      - name: Run commands
        env:
          GITHUB_TOKEN: ${{ steps.app-token.outputs.token }}
        run: |
          # Your commands here
```

### Option B: Two Jobs (With Container)

Use this pattern when you need to run steps inside a Docker container. The `actions/create-github-app-token` action doesn't work inside custom containers, so we generate the token in a separate job first:

```yaml
jobs:
  generate-token:
    runs-on: ubuntu-latest
    outputs:
      token: ${{ steps.app-token.outputs.token }}
    steps:
      - name: Generate GitHub App Token
        id: app-token
        uses: actions/create-github-app-token@v2
        with:
          app-id: ${{ vars.COPYBARA_APP_ID }}
          private-key: ${{ secrets.COPYBARA_PRIVATE_KEY }}
          repositories: copybara-demo-A,copybara-demo-B

  copybara-job:
    needs: generate-token
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/anipos/copybara-docker-image

    steps:
      - name: Checkout code
        uses: actions/checkout@v4
        with:
          token: ${{ needs.generate-token.outputs.token }}

      - name: Configure Git
        env:
          GITHUB_TOKEN: ${{ needs.generate-token.outputs.token }}
        run: |
          git config --global user.name "Copybara Bot"
          git config --global user.email "copybara@example.com"
          git config --global credential.helper store
          echo "https://x-access-token:${GITHUB_TOKEN}@github.com" > ~/.git-credentials

      - name: Run Copybara
        env:
          GITHUB_TOKEN: ${{ needs.generate-token.outputs.token }}
        run: |
          copybara migrate copy.bara.sky workflow_name \
            --git-destination-url="https://x-access-token:${GITHUB_TOKEN}@github.com/org/repo.git"
