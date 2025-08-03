# AI Contribution Guidelines

RouteForcePro supports collaboration from both human developers and AI agents (e.g., GitHub Copilot, ChatGPT).

## Purpose

To ensure transparency, accountability, and quality control, this guide sets expectations for AI-generated contributions.

## Labeling Expectations

- Mark AI-generated pull requests with the `ai-generated` label.
- Mention the AI system used (e.g., “Generated via ChatGPT-4o on 2025-08-03”) in the PR body.

## Scope of Acceptable AI Use

- ✅ Code generation (logic scaffolding, tests, boilerplate)
- ✅ Documentation drafting (README, CONTRIBUTING, etc.)
- ❌ Legal documents or license files
- ❌ Security-sensitive patches (e.g., cryptography, auth)

## Human Responsibility

Even if AI generates the code:
- A human must review and validate the result.
- PRs must include working test coverage for affected logic.