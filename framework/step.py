from framework.logger import logger
import logging

step_no = 1
_steps = []
_current_phase = "Test"
_test_class_name = None
_test_method_name = None


def set_phase(phase, test_class_name=None, test_method_name=None):
    """Set the current test phase with test class and method names.
    
    Args:
        phase: "Setup", "Test", or "Teardown"
        test_class_name: Name of the test class (e.g., "TestSysmon")
        test_method_name: Name of the test method (e.g., "test_sysmon")
    """
    global _current_phase, _test_class_name, _test_method_name
    _current_phase = phase
    _test_class_name = test_class_name
    _test_method_name = test_method_name


def clear_steps():
    global _steps, step_no
    _steps = []
    step_no = 1


def get_steps():
    """Return a copy of recorded steps.

    Each step is returned as a tuple: (phase_label, message).
    """
    return list(_steps)


def get_phase_label():
    """Generate phase label in format: setup.test_name or TestClass.test_name or teardown.test_name"""
    if not _test_method_name:
        return _current_phase
    
    if _current_phase == "Setup":
        return f"setup.{_test_method_name}"
    elif _current_phase == "Teardown":
        return f"teardown.{_test_method_name}"
    else:  # Test
        return f"{_test_class_name}.{_test_method_name}"


def step(message):
    global step_no

    print(f"[STEP {step_no}] {message}")
    
    # Create a log record with phase information
    record = logger.makeRecord(
        logger.name,
        logging.INFO,
        "step.py",
        0,
        f"STEP {step_no}: {message}",
        (),
        None
    )
    phase_label = get_phase_label()
    record.phase = phase_label
    logger.handle(record)

    # store both phase and message so callers can slice by phase
    _steps.append((phase_label, message))
    step_no += 1
