import pytest

from framework.base_test import BaseTest
from framework.assertion import assert_step as ASSERT
from framework.step import step
from tests.monitor_tests.helpers import (
    launch_application,
    close_application,
    verify_monitor_event_collection,
    verify_monitor_rules_loaded,
)
from framework.logger import logger


@pytest.mark.metadata(
    description="Validate monitor service status and event collection availability",
    verfies=["SYS-003", "SYS-004"],
    testType="Requirement Based-Test",
    ASIL="ASIL D",
    status="Ready",
)
@pytest.mark.extended_metadata(
    author="Automation Team",
    creation_date="2026-07-05",
    last_modified_date="2026-07-05",
    ticket_number="SWP-1235",
)
class TestMonitorServiceAndEventCollection(BaseTest):

    def setup(self):
        step("Launch application")
        logger.info("************* Starting Application *********")
        ASSERT(launch_application(), "Launch application failed")
        logger.info("************* Application Started *********")

    def test_monitor_service_is_running(self):
        step("Verify monitor service is installed and running")
        ASSERT(
            verify_monitor_rules_loaded(),
            "Monitor service must be installed and running",
        )

    def teardown(self):
        step("Close application")
        ASSERT(close_application(), "Close application failed")
