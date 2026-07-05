import pytest

from framework.base_test import BaseTest
from framework.assertion import assert_step as ASSERT
from framework.step import step
from tests.monitor_tests.helpers import (
    launch_application,
    close_application,
    verify_python_process_is_running,
)

@pytest.mark.metadata(
    description="Verify the Python process lifecycle during test execution",
    verfies=["SYS-001"],
    testType="Requirement Based-Test",
    ASIL="ASIL D",
    status="Ready",
)
@pytest.mark.extended_metadata(
    author="Automation Team",
    creation_date="2026-07-05",
    last_modified_date="2026-07-05",
    ticket_number="SWP-1234",
)
class TestPythonApplicationLifecycle(BaseTest):

    def setup(self):
        step("Launch application")
        ASSERT(launch_application(), "Launch application failed")

    def test_python_process_is_running(self):
        step("Verify Python process is running")
        ASSERT(
            verify_python_process_is_running(),
            "Python process should be running during test execution",
        )

    def teardown(self):
        step("Close application")
        ASSERT(close_application(), "Close application failed")

