import os
import sys

from framework.base_test import BaseTest
from framework.step import step
from framework.utils import is_process_running
from framework.assertion import assert_step


class TestSysmonn(BaseTest):

    def setup(self):
        step("Launch Application")
        assert_step(False, f" process is running")

    def test_sysmo(self):
        step("Start Testing")
        step("Verify sysmon")
        executable = os.path.basename(sys.executable)
        assert_step(True, f"{executable} process is running")

    def teardown(self):
        step("Close Application")
        
        executable = os.path.basename(sys.executable)
        assert_step(False, f"{executable} process is running")

