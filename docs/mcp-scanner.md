# MCP Scanner (model-usage) — README

This document explains the repository's MCP scanner that detects Model Context Protocol (MCP) preview model usage and related configuration keys in pull requests.

Summary
- Purpose: detect references to preview MCP models (for example `copilot/gpt-5-mini-preview`) and surface them to reviewers.
- Primary artifacts:
  - `.github/workflows/mcp-model-usage.yml` — scans changed files, posts snippet-containing PR comments, and applies `mcp` label.
  - `.github/workflows/mcp-scan-check.yml` — PR check that runs the local test harness and fails if markers are found.
  - `.github/mcp-scan-test.sh` — local scanner test harness used for validation.

How it works (high level)
- On PRs and pushes the scanner computes the changed files, filters to likely text/config files in whitelisted directories, and searches for explicit model IDs or MCP-related config keys.
- If matches are found the workflow will report snippets in a PR comment and, depending on the workflow, add the `mcp` label or fail the check.

Why this exists
- Prevent accidental or unsupported usage of preview MCP models in production code.
- Give reviewers and maintainers visibility when MCP preview models are referenced so appropriate approvals or rollouts can be coordinated.

What to do when your PR is flagged
1. Inspect the PR comment and the snippet(s) posted by the scanner.
2. If the reference is intentional (for testing or accepted opt-in), add a short comment explaining the intent and request re-scan if needed.
3. If the reference is accidental, remove or redact it and push an update.
4. If you believe a false positive occurred, ping the maintainers and include the file(s) that triggered the scan.

Requesting opt-in or admin approval
- Use `.github/ISSUE_TEMPLATE/mcp-preview-request.md` to request administrator approval for preview models when necessary.

Contact
- For questions or to report scanner issues: @maintainers (or open an issue labeled `mcp`).

Notes and limitations
- The scanner uses grep-based matching; it may miss binary or unusual encodings and is tuned for source/config files.
- We intentionally whitelist common source and config directories to reduce noise; if you have legitimate exceptions, request an allowlist entry.
