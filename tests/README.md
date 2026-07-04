# Tests Folder README

This folder contains pytest integration files and user test cases.

Files:

- `__init__.py`
  - Marks the `tests` folder as a Python package.

- `conftest.py`
  - Defines pytest hooks for the custom reporting behavior.
  - Clears step logs before each test.
  - Enforces required metadata markers on each test class.
  - Supports custom failure handling and report generation.

- `run_tests.py`
  - A helper script for running tests from the repository root.
  - Defaults to executing `tests/sysmon_tests/` when no arguments are supplied.
  - When run directly, pytest is invoked against the `tests/sysmon_tests` folder.

- `test_sysmon.py`
  - Example test class showing framework use.
  - Uses `BaseTest` and `step()` to define setup, test, and teardown actions.
  - Includes metadata decorators to satisfy the required test metadata rules.

## How tests are executed

1. `run_tests.py` is invoked with or without explicit test paths.
2. It resolves the default path to `tests/sysmon_tests` if no args are given.
3. `pytest.main(...)` runs the selected tests.
4. The helper runner `tests/sysmon_tests/run_tests.py` may also be executed directly by Bazel.
5. Each test records phase-aware step output during `setup`, `call`, and `teardown`.
6. Test artifacts are generated after the run.

## Test artifacts

- `test.log`
  - Written by the runner with timestamped step execution lines.
  - Includes per-test execution details and a consolidated summary.

- `report.xml`
  - A JUnit-style XML report generated at runtime.

When running directly, both files are written to `output/`.
When running under Bazel, they are written into Bazel's preserved output directory.

## Bazel support

The repository defines a root Bazel target named `//:main_test_target`.
This target refers to the Bazel package `//tests/sysmon_tests:sysmon_test`.
That package contains the actual Python test target and its sources.

Use:

```bash
bazel test //:main_test_target --test_output=errors
```

This target executes all cases under `tests/sysmon_tests/` and preserves the generated `test.log` and `report.xml` files in Bazel's output tree.
