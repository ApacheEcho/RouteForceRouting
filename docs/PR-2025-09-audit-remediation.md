Title: Frontend dependency audit findings and remediation plan

Summary
-------

This PR documents the current frontend `npm audit` findings and proposes a safe remediation path. The CI now uploads `frontend-audit.json` as a non-blocking artifact so reviewers can inspect the full audit output.

Findings
--------

- `npm audit` reports 9 vulnerabilities (6 high, 3 moderate) primarily in transitive dependencies under `react-scripts` (svgo, @svgr, nth-check, postcss, webpack-dev-server).
- Running `npm audit fix --force` would perform a breaking upgrade (react-scripts) and may break the build.

Proposed plan (safe path)
-------------------------

1. Immediate (this PR):
   - Treat audit output as informational and publish it in CI (`frontend-audit.json`).
   - Document risks in `SECURITY_RISKS.md` and set an internal ticket to upgrade in the next release.

2. Near term (next sprint):
   - Attempt controlled upgrades of `react-scripts` to the latest stable. Run the full test suite and fix regressions.
   - If direct upgrade fails due to transitive dependencies, attempt targeted upgrades of the transitive packages.

3. Medium term (recommended):
   - Migrate the frontend from Create-React-App (`react-scripts`) to Vite or Next.js. This reduces transitive dependency surface and modernizes developer experience.

CI changes in this PR
---------------------

- `.github/workflows/ci.yml`: runs `npm audit --json` and uploads `frontend-audit.json` as a non-blocking artifact.

How to validate locally
-----------------------

Run frontend audit and tests locally:

```bash
npm ci
npm audit --json > frontend-audit.json || true
npm test -- --watchAll=false
```

Next steps (I can do this):
- Attempt controlled `react-scripts` upgrade and fix breakages.
- Scaffold a CRA->Vite migration branch with minimal changes and smoke-test the build.

Please review and let me know which path you want me to take next.
