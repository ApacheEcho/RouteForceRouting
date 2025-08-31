---
name: MCP Preview Model Request
about: Request admin approval to enable preview MCP models (e.g., copilot/gpt-5-mini-preview) for this repository
title: 'Request: Enable copilot/gpt-5-mini-preview for RouteForceRouting'
labels: ['mcp','admin-request']
assignees: []
---

Please enable the `copilot/gpt-5-mini-preview` model for the RouteForceRouting MCP sampling list (context7) so the team can test preview model behavior.

Proposed change:
- workspace: add `copilot/gpt-5-mini-preview` to `chat.mcp.serverSampling.Global in Code: context7.allowedModels` for the `RouteForceRouting` repo.

Rationale:
- Evaluate improvements in code completion, routing-specific reasoning, and latency.

Rollback plan:
- Remove the model from `allowedModels` if issues are observed.

Contact:
- [Your name and contact]

Additional notes:
- Project trust: ensure `.codex/config.toml` has an entry marking this repo as `trusted` if required by policy.
