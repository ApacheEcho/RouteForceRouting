# Security risks and remediation options

This document records the current frontend dependency audit findings and recommended safe remediation steps.

Summary (as of run):

- Total vulnerabilities reported by `npm audit`: 9 (6 high, 3 moderate)
- Affected tooling: transitive dependencies under `react-scripts` (svgo, @svgr, nth-check, postcss, webpack-dev-server)

Why we chose the safe path:

- The critical vulnerabilities are transitive and rooted in `react-scripts` and its toolchain. Fully fixing them requires a major upgrade or migration (for example upgrading `react-scripts` or migrating from Create-React-App to Vite/Next).
- Running `npm audit fix --force` would attempt a breaking change (upgrade `react-scripts` to an incompatible version) which risks breaking the build and introducing immediate regressions.

Recommended remediation options:

1) Short-term (current - low risk):
   - Keep current dependencies, monitor for exploit reports, and treat audit findings as informational. Add `npm audit` to CI as a non-blocking artifact. Schedule upgrade work in the next release cycle.
   - Restrict developer access to untrusted sites and ensure contributors run `npm ci` in CI rather than `npm install` locally when preparing production builds.

2) Medium-term (moderate effort):
   - Attempt controlled upgrades of `react-scripts` to the latest stable version. Run full test suites and fix any breaking changes.
   - If `react-scripts` upgrades are blocked, upgrade or replace transitive dependencies (e.g., svgo, css-select) where possible.

3) Long-term (recommended):
   - Migrate from Create React App (`react-scripts`) to a modern bundler like Vite or a framework like Next.js. This reduces transitive dependency surface and simplifies upgrades.

CI changes made:

- CI will be updated to publish `npm audit --json` output as a non-blocking artifact so reviewers can inspect it.

Notes:

- This repo's frontend tests pass locally and CI continues to run tests; the audit findings are visible and should be tracked as a project risk.

If you'd like, I can attempt the medium-term option (controlled upgrades) now or scaffold a CRA->Vite migration plan.

