import os
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from framework.step import clear_steps, get_steps

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(os.environ.get("TEST_UNDECLARED_OUTPUTS_DIR", ROOT / "output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = OUTPUT_DIR / "report.xml"
LOG_PATH = OUTPUT_DIR / "test.log"


def pytest_sessionstart(session):
    # Clear report and test log for fresh run
    REPORT_PATH.write_text("", encoding="utf-8")
    LOG_PATH.write_text("", encoding="utf-8")


def pytest_runtest_setup(item):
    clear_steps()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    # Only write report after teardown completes (to capture all steps)
    # Write if teardown is done OR if call failed and teardown won't run
    write_report = False
    if rep.failed:
        if rep.when == "teardown":
            write_report = True
        elif rep.when == "call":
            # For call failures, still write so we don't lose info, but will be overwritten if teardown fails
            write_report = True
    
        # For now, only write after teardown to include all steps
        write_report = (rep.when == "teardown" and rep.failed) or (rep.when == "call" and rep.failed)
    # Write report during teardown phase if test failed during call phase
    if rep.when == "teardown" or rep.failed:
        steps = get_steps()
        
        # Find the failed step and get the failure reason
        failed_step_index = None
        failure_reason = ""
        for idx, step in enumerate(steps, start=1):
            if "ASSERTION FAILED" in step:
                failed_step_index = idx
                # Extract the reason after "ASSERTION FAILED: "
                failure_reason = step.replace("ASSERTION FAILED: ", "")
        
        # Parse test class and method
        test_nodeid = item.nodeid
        parts = test_nodeid.split("::")
        test_file = parts[0]
        test_class = parts[1] if len(parts) > 1 else ""
        test_method = parts[2] if len(parts) > 2 else ""
        
        # Build XML report content
        report_lines = []
        report_lines.append(f"class {test_class}(BaseTest):")
        report_lines.append("")
        
        # Add setup steps (first step is usually setup)
        setup_steps = steps[:1]  # First step is setup
        if setup_steps:
            report_lines.append("    def setup(self):")
            for step in setup_steps:
                report_lines.append(f"        step(\"{step}\")")
            report_lines.append("")
        
        # Add test method steps - include all steps (test + teardown)
        report_lines.append(f"    def {test_method}(self):")
        test_and_teardown_steps = steps[1:]  # All steps after setup
        for idx, step in enumerate(test_and_teardown_steps, start=2):
            if idx == failed_step_index:
                # Mark the failed assertion
                if "ASSERTION FAILED" in step:
                    report_lines.append(f"        assert_step(condition, \"{failure_reason}\")  ---FAILED")
                else:
                    report_lines.append(f"        step(\"{step}\")")
            else:
                report_lines.append(f"        step(\"{step}\")")
        
        # Add failure reason at the end
        if failure_reason:
            report_lines.append(f"        <Reason of failure: {failure_reason}>")
        
        report_lines.append("")
        report_content = "\n".join(report_lines)
        
        # Write to report.xml as plain text
        REPORT_PATH.write_text(report_content, encoding="utf-8")
