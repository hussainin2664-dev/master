# Test Framework Project

This repository implements a custom Python test framework and reporting system on top of `pytest`.
It includes framework utilities, custom metadata checks, phase-aware step logging, and generated test reports.

## Project structure

- `framework/`
  - Core framework modules for assertions, logging, and test lifecycle control.
  - See `framework/README.md` for implementation details.

- `tests/`
  - Pytest integration folder and example test packages.
  - Contains `tests/sysmon_tests/` for grouped Sysmon test cases.
  - See `tests/README.md` for details on test package structure and Bazel usage.

- `output/`
  - Generated artifacts from test runs.
  - Output files include `output/report.xml` and `output/test.log` when running directly.

- `pytest.ini`
  - Registers custom pytest markers used by the test metadata system.

- `requirements.txt`
  - Python dependencies required by the test framework.

- `requirements_lock.txt`
  - Locked package versions for reproducible environments.

- `run_test.sh`
  - Convenience shell script to run tests from a Unix-like terminal.

- `process_of_test_execution.txt`
  - A detailed execution-flow document describing how tests are triggered, dependencies are resolved, and reports are generated.

## Current behavior

- The framework records named steps during each test phase (`setup`, `test`, `teardown`).
- Test failures in teardown are reported as `ERROR` and are included in the final summary.
- A custom runner writes a timestamped `test.log` and a JUnit-style `report.xml` after execution.
- When running under Bazel, these files are written into Bazel's preserved test output directory.

## Running tests locally

From the project root using Python:

```bash
./.venv/Scripts/python.exe run_tests.py
```

From a Unix-like shell:

```bash
bash run_test.sh
```

When run directly, the runner writes artifacts to `output/report.xml` and `output/test.log`.

## Running tests with Bazel

Use Bazel with the root test target:

```bash
bazel test //:main_test_target --test_output=errors
```

This executes the `tests/sysmon_tests` package through the root Bazel target and preserves test artifacts in Bazel test output directories. The actual report files are written to the Bazel-managed output location, not necessarily the repo `output/` folder.

## Notes

- `//:main_test_target` is a Bazel `test_suite` target that runs the test package defined in `tests/sysmon_tests/`.
- The test runner is responsible for generating both `test.log` and `report.xml`.
- See `tests/README.md` for package-level execution details and `framework/README.md` for internal framework behavior.
# master
# master
