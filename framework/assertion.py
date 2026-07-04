from framework.step import step


class AssertionError(Exception):
    """Custom assertion error to halt test execution"""
    pass


def assert_step(condition, message):
    """
    Assert condition and stop execution if it fails.
    If condition is True, continue to next step.
    If condition is False, raise AssertionError with message.
    
    Args:
        condition: Boolean condition to check
        message: Message to display on assertion failure
    
    Raises:
        AssertionError: If condition is False
    """
    if not condition:
        step(f"ASSERTION FAILED: {message}")
        raise AssertionError(message)
    step(f"ASSERTION PASSED: {message}")
