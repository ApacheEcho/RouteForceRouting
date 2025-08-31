# Enabling Preview Models (e.g., GPT-5 mini) for this Repo

This document describes how developers can opt this repository and their VS Code workspace into preview/experimental MCP models (for example `copilot/gpt-5-mini-preview`). It covers workspace settings, user settings, repository trust, and an optional admin notification template.

## 1) Workspace-level (recommended for team-wide opt-in)
Add the allowed MCP models to the workspace settings at `.vscode/settings.json`.

Example snippet:

```jsonc
{
  "chat.mcp.serverSampling": {
    "Global in Code: context7": {
      "allowedModels": [
        "copilot/gpt-4.1",
        "copilot/gpt-5-mini-preview"
      ]
    }
  }
}
```

- Place the snippet inside the existing JSON object (merge; do not replace the entire file unless intentional).
- After updating, teammates should reload VS Code or restart the MCP/session to pick up the change.

## 2) User-level (local opt-in)
If you prefer to enable preview models only for your machine, edit your user `settings.json` in VS Code (File > Preferences > Settings > click the `{}` icon to open JSON). Add the same `chat.mcp.serverSampling` block shown above.

Example (user `settings.json`):

```jsonc
"chat.mcp.serverSampling": {
  "Global in Code: context7": {
    "allowedModels": [
      "copilot/gpt-4.1",
      "copilot/gpt-5-mini-preview"
    ]
  }
}
```

Notes:
- Editing the user-level settings modifies only your VS Code client and does not affect the repo or other developers.
- If the setting already exists, append the preview model to the `allowedModels` array.

## 3) Repository trust (.codex/config.toml)
Some clients check for project trust before enabling experimental or high-risk features. If your environment uses `.codex/config.toml`, ensure your project path is marked `trusted`.

Example `~/.codex/config.toml` entry:

```toml
[projects."/Users/you/your-repo-path"]
trust_level = "trusted"
```

## 4) Admin approval and MCP rollout
In some organizations, MCP or model previews require central rollout approval. Use the template below to request activation from your MCP admins.

**Admin request template**

```
Subject: Request to enable copilot/gpt-5-mini-preview for RouteForceRouting

Hi team,

Please enable the `copilot/gpt-5-mini-preview` model for the RouteForceRouting MCP sampling list (context7) so the team can test preview model behavior. Proposed change:

- workspace: add `copilot/gpt-5-mini-preview` to `chat.mcp.serverSampling.Global in Code: context7.allowedModels` for the `RouteForceRouting` repo.
- rationale: evaluate improvements in completion quality and latency for routing-related tasks.
- rollback: remove model from allowedModels if issues are observed.

Happy to provide logs or reproduce issues if needed.

Thanks,
[Your Name]
```

## 5) Troubleshooting
- If the model doesn't appear: reload VS Code, sign out/in of Copilot/MCP, and ensure your client plugin versions are up to date.
- If you get access or permission errors: contact MCP administrator; provide the admin request template above.

---

If you'd like, I can open a PR that adds this document to the repository and optionally update `.github/ISSUE_TEMPLATE` or the developer README with a link. Tell me how you'd like to proceed.
