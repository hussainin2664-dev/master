# Test Framework Project

This repository contains a custom Python test framework built on top of `pytest`.
It includes reusable framework utilities, step-based test reporting, failure-aware teardown handling, and Bazel integration.

## Repository structure

- `framework/`
  - Core framework modules for assertions, logging, test lifecycle management, and step recording.
  - See `framework/README.md` for implementation details.

- `tests/`
  - Pytest integration files and example test packages.
  - Contains `tests/monitor_tests/`, which implements the monitor test package and custom test runner.
  - See `tests/README.md` for test execution and artifact behavior.

- `output/`
  - Generated artifacts from direct and Bazel test runs.
  - Current output files include `output/report.xml`, `output/test.log`, and `output/pytest_report.xml`.

- `pytest.ini`
  - Configures pytest markers and enables custom test metadata validation.

- `requirements.txt`
  - Python dependencies required by the framework and tests.

- `requirements_lock.txt`
  - Locked package versions for reproducible environments.

- `run_test.sh`
  - Shell script wrapper for running tests from a Unix-like shell.

- `run_tests.py`
  - Repository-level Python entry point for running tests.

- `process_of_test_execution.txt`
  - Documentation describing test execution flow, reporting behavior, and Bazel target mapping.

## What this project provides

- A test framework that records named step output during `setup`, `call`, and `teardown` phases.
- Custom assertion behavior that logs passed and failed assertions as step events.
- A custom runner that generates a readable `output/report.xml` and a timestamped `output/test.log`.
- Bazel integration that preserves generated artifacts in the Bazel test output directory.

## Run tests locally

From the repository root:

```bash
bash run_test.sh tests/monitor_tests/
```

Or directly with Python:

```bash
./.venv/Scripts/python.exe tests/monitor_tests/run_tests.py
```

Both commands write output to the repository-level `output/` folder.

## Run tests with Bazel

Use the root Bazel target:

```bash
bazel test //:main_test_target --test_output=errors
```

For a fresh execution that ignores cached test results, use:

```bash
bazel test //:main_test_target --test_output=errors --nocache_test_results
```

This runs the `tests/monitor_tests` package through Bazel and preserves the generated artifacts.

## Output files

- `output/report.xml`
  - Custom readable report with test phase steps and failure summaries.

- `output/test.log`
  - Timestamped log of test execution, including step output and overall summary.

- `output/pytest_report.xml`
  - Standard pytest JUnit XML output for CI tools.

## Notes

- The Bazel test target `//:main_test_target` is a `test_suite` that depends on `//tests/monitor_tests:monitor_test`.
- The framework supports phase-aware logging and teardown failure handling.
- `process_of_test_execution.txt` explains the full runtime flow and output generation.
