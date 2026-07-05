# Tests Folder README

This folder contains the pytest integration layer and example user tests.
It also defines the package-level test runner used for local execution and Bazel integration.

## Purpose

- Keep test package code separate from framework internals.
- Provide custom pytest hooks for test metadata validation and failure handling.
- Generate readable test artifacts for both local and Bazel runs.

## Main files

- `__init__.py`
  - Marks `tests/` as a Python package.

- `conftest.py`
  - Implements custom pytest hooks for the project.
  - Clears framework step state before each test.
  - Enforces required metadata markers on each test.
  - Writes readable failure reports and ensures teardown errors are reported correctly.

- `run_tests.py`
  - Local test runner entry point.
  - Uses `pytest.main(...)` to execute tests under `tests/monitor_tests/`.
  - Defaults to the `tests/monitor_tests` package when no arguments are provided.

- `tests/monitor_tests/`
  - Contains the actual monitor test package.
  - Includes a package-level runner, test cases, helper utilities, and custom reporting behavior.

## How tests run

1. `run_tests.py` is executed from the repository root.
2. If no arguments are provided, it runs `tests/monitor_tests/`.
3. Pytest loads `tests/conftest.py` and applies the custom hooks.
4. The framework records test steps for `setup`, `call`, and `teardown` phases.
5. The runner writes the final artifact files after the test session completes.

## Artifacts produced

- `output/test.log`
  - A timestamped execution log with one line gap between test cases.
  - Includes per-test step details and an overall summary.

- `output/report.xml`
  - A custom readable XML-style report that shows test phase output and failure reasons.

- `output/pytest_report.xml`
  - Standard Pytest JUnit XML output for CI tools and report parsers.

## Running tests

### Direct execution

```bash
bash run_test.sh tests/monitor_tests/
```

### Python execution

```bash
./.venv/Scripts/python.exe tests/monitor_tests/run_tests.py
```

### Bazel execution

```bash
bazel test //:main_test_target --test_output=errors
```

For a fresh Bazel run that ignores cache:

```bash
bazel test //:main_test_target --test_output=errors --nocache_test_results
```

## Test metadata

Each test should include the required metadata markers defined in `conftest.py`.
This repository validates metadata before tests execute and raises errors for missing or incomplete metadata.
