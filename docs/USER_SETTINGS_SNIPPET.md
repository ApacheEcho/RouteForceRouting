# User settings snippet for enabling preview MCP models

To enable preview models locally in your VS Code user settings, open your user `settings.json` (File > Preferences > Settings > click the `{}` icon) and add the following snippet inside the top-level JSON object.

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

How to apply:
1. If a `chat.mcp.serverSampling` block already exists, append `"copilot/gpt-5-mini-preview"` to the `allowedModels` array.
2. Save the file and reload VS Code.
3. If the model does not appear, sign out/in of Copilot/MCP or restart the MCP client.

Notes:
- This modifies only your local VS Code configuration and does not affect other developers.
- If your organization requires project trust, ensure your project is listed as `trusted` in `~/.codex/config.toml`.
