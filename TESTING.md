# Testing Guide

## Quick Commands

- All tests:
  - `pytest -q`
- Fast subset (skips slow tests):
  - `pytest -m "not slow" -q`
- Only slow tests (run locally or in nightly CI):
  - `pytest -m slow -q --durations=10`

## Slow Tests

The following suites are marked with `@pytest.mark.slow`:

- `tests/test_advanced.py` — broad coverage; heavier mocking and path coverage.
- `tests/test_genetic_edge_case.py` — integration harness; tests a genetic optimization compat endpoint.

In CI:

- The main test job runs fast suites: `-m "not slow" -n auto` (parallelized).
- A separate `test-long` job runs slow suites with longer timeouts.
- A nightly workflow runs slow tests and files GitHub issues if modules fail.

## Tips

- Use `-vv -s --maxfail=1` for debugging a failing test.
- To profile slow tests: `pytest --durations=10`.
- Ensure `ROUTEFORCE_TESTING=1` is set (conftest does this) for network-free integrations.

