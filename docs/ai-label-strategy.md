# AI Label Strategy

To distinguish AI-generated work from human-authored contributions, the following labels and metadata policies are enforced.

## Labels

| Label | Purpose |
|-------|---------|
| `ai-generated` | Code, docs, or issues authored with assistance from an AI |
| `copilot`      | PRs or commits generated with GitHub Copilot |
| `chatgpt`      | PRs or commits created or edited using ChatGPT |
| `human-reviewed` | Indicates the AI contribution was audited by a human |

## Metadata Tags (PRs)

PR templates include:
- `AI-generated?` checkbox
- Notes field to specify tool/version (e.g., GPT-4o, Claude 3)

## Automation

GitHub Actions will:
- Auto-apply `ai-generated` label to PRs with AI attribution
- Reject PRs marked as AI-generated but lacking reviewer assignment