# CI Overview

## Jobs

- `test`: fast subset of tests (excludes `@pytest.mark.slow`) and coverage.
  - Parallelized via `pytest-xdist` to reduce runtime.
  - Uploads `coverage.xml` and `htmlcov/` as artifacts.
- `test-long`: runs slow tests (`-m slow`) with extended timeout.
  - Does not block the main job; intended to catch long-running regressions.
- `security`: Trivy filesystem scan; uploads SARIF to GitHub Security tab on `main`.
- `build`: Docker build & push on `push`.

## Nightly

- Workflow: `.github/workflows/nightly-long-tests.yml`
- Runs slow suites with timings and creates a GitHub issue if failures occur.
- Optional notifications:
  - Set a repository variable `NIGHTLY_MENTION` (e.g., `@org/team` or `@username`) to be appended to issues.

## Local Tips

- Mark slow tests with `@pytest.mark.slow` so they run in the long job or nightly.
- Use `pytest -m "not slow" -n auto` locally to simulate the fast job.

