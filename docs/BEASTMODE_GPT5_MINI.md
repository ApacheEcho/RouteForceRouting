Beast Mode — GPT-5 Mini tuning

Purpose
- Short guide for optimizing "Beast Mode" workflows to use `copilot/gpt-5-mini-preview` as the fast, low-latency primary model with `copilot/gpt-4.1` as a fallback for heavy tasks.

Recommended configuration (workspace/user)
- Add the following snippet to your `settings.json` (workspace or user) to prefer GPT-5 Mini for Beast Mode:

```
"chat.mcp.modelPreferences": {
  "beastMode": {
    "primary": "copilot/gpt-5-mini-preview",
    "fallback": "copilot/gpt-4.1",
    "maxTokens": 512,
    "temperature": 0.2,
    "top_p": 0.8,
    "structuredOutput": true
  }
}
```

Practical tuning tips
- Use short system prompts and keep static instructions in repo docs.
- Summarize large files first and feed concise chunks to GPT-5 Mini.
- Keep token budgets small (256–512) and temperature low (0.15–0.35) for deterministic code outputs.
- For long planning or high-risk operations (infra, secrets), automatically promote to `copilot/gpt-4.1`.
- Validate machine-readable outputs with a small verifier prompt; if missing fields, re-request a concise correction.

Operational notes
- Monitor latency, token usage, and error rates per model.
- Batch similar small tasks and cache repeated prompts.

See also
- `.github/CODELLAUNCH.md` for opt-in procedures and trust guidance.
