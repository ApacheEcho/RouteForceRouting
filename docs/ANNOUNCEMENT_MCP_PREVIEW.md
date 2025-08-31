# Announcement: MCP Preview Model Opt-in (copilot/gpt-5-mini-preview)

I'm enabling preview MCP model opt-in for this repository to let the team evaluate `copilot/gpt-5-mini-preview`.

What changed
- Added documentation: `.github/CODELLAUNCH.md`
- Added user snippet: `docs/USER_SETTINGS_SNIPPET.md`
- Added admin issue template: `.github/ISSUE_TEMPLATE/mcp-preview-request.md`
- Updated README to link to the CODELLAUNCH guide
- Workspace opt-in: `.vscode/settings.json` includes `copilot/gpt-5-mini-preview` in `chat.mcp.serverSampling`

How to try it locally
1. Pull `main` and ensure workspace settings are applied, or add the snippet to your user settings as described in `docs/USER_SETTINGS_SNIPPET.md`.
2. Reload VS Code and sign in to Copilot/MCP.
3. Check the model list in your Copilot/MCP client for `copilot/gpt-5-mini-preview`.

Notes
- If you see any issues, revert the workspace setting or remove the model from `allowedModels`.
- Since I'm the admin, I assume responsibility for monitoring and rolling back if needed.

PR: https://github.com/ApacheEcho/RouteForceRouting/pull/100
