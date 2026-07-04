import os
import sys

from framework.base_test import BaseTest
from framework.step import step
from framework.utils import is_process_running
from framework.assertion import assert_step
import pytest


@pytest.mark.metadata(
    
    description="Test Sysmon functionality",
    verfies=[],#---> Requierement IDs
    testType="Requierement Based-Test", #requiredment based or experiance based test
    ASIL="ASIL D", #ASIL A/B/C/D
    status="Ready" #Ready ,Design ,Obsolete
)
@pytest.mark.extended_metadata(
    author="Your Name",
    creation_date="2024-06-01",
    last_modified_date="2024-06-01",
    ticket_number="SWP-1234",
)
class TestDummy(BaseTest):

    def setup(self):
        step("Launch Application")
        assert_step(True, f" process is running")

    def test_dummy(self):
        step("Start Testing")
        step("Verify sysmon")
        executable = os.path.basename(sys.executable)
        assert_step(True, f"{executable} process is running")

    def teardown(self):
        step("Close Application")
        
        executable = os.path.basename(sys.executable)
        assert_step(False, f"{executable} process is running")

