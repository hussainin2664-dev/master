# Framework Folder README

This folder contains the core framework code used by tests in this project.
The framework helps record test steps, enforce lifecycle phases, log output, and support custom assertion behavior.

## Files and What They Do

### `__init__.py`
- Marks `framework/` as a Python package.
- Allows import statements like `from framework.step import step`.

### `assertion.py`
- Defines `assert_step(condition, message)` for framework assertions.
- When the condition is `True`, it logs a passing assertion step.
- When the condition is `False`, it logs a failed assertion step and raises a framework `AssertionError`.
- This makes assertion failures appear as step events as well as test failures.

### `base_test.py`
- Provides `BaseTest`, the base class for test classes.
- Uses pytest autouse fixtures to manage test phases:
  - `lifecycle`: runs `setup()`, then the test method, with correct phase tracking.
  - `_ensure_teardown`: always runs `teardown()` at the end, even if `setup()` or the test body failed.
- This ensures teardown steps are captured and reported reliably.

### `logger.py`
- Configures the logger used by `framework.step`.
- Initializes a `logger` object and a custom formatter.
- Writes framework step output to `output/test.log` for later review.

### `step.py`
- Defines the main step recording API.
- `step(message)` records a message, prints it, and logs it with current phase context.
- `set_phase(phase, test_class_name, test_method_name)` sets the current phase:
  - `Setup`
  - `Test`
  - `Teardown`
- `get_steps()` returns recorded steps as tuples of `(phase_label, message)`.
- `clear_steps()` resets step history before each test.

### `config.py`
- Holds framework configuration values.
- Use it for shared settings or test environment constants.
- This file is currently a placeholder for future configuration needs.

### `utils.py`
- Contains helper functions for framework test logic.
- Typical use cases include process checks, path helpers, or reusable validation routines.
- If not currently used, it is a place to add common utilities later.

## How It Works Together
- `BaseTest` ensures the current phase is set when tests run.
- `step.py` records each step with a phase label and writes it to `output/test.log`.
- `assertion.py` uses `step()` to log assertion results before raising failures.
- `logger.py` ensures console and file output are formatted consistently.
- `tests/sysmon_tests/run_tests.py` generates the final `test.log` and `report.xml` files after execution.
- The test suite and `tests/conftest.py` use these components to build test reports and enforce teardown behavior.

## What to Read Next
- `tests/README.md`: explains the test folder, custom pytest hooks, and the sample test file.
- `output/README.md`: describes the generated report files and logs.
