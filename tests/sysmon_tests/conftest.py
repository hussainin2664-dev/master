import os
from pathlib import Path

import pytest

try:
    import _pytest.reports as _pytest_reports

    def _count_towards_summary(self):
        return getattr(self, "_count_towards_summary", True)

    _pytest_reports.BaseReport.count_towards_summary = property(_count_towards_summary)
except ImportError:
    _pytest_reports = None

from framework.step import clear_steps, get_steps

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = Path(os.environ.get("TEST_UNDECLARED_OUTPUTS_DIR", ROOT / "output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_PATH = OUTPUT_DIR / "report.xml"
LOG_PATH = OUTPUT_DIR / "test.log"
FAILED_BEFORE_TEARDOWN = set()


def pytest_sessionstart(session):
    # Clear report and test log for fresh run
    REPORT_PATH.write_text("", encoding="utf-8")
    LOG_PATH.write_text("", encoding="utf-8")
    FAILED_BEFORE_TEARDOWN.clear()


def pytest_runtest_setup(item):
    clear_steps()


def pytest_collection_modifyitems(config, items):
    missing_metadata = []
    missing_keys = []
    required_metadata_keys = ["description", "verfies", "testType", "ASIL", "status"]
    required_extended_keys = ["author", "creation_date", "last_modified_date", "ticket_number"]

    for item in items:
        metadata = next(item.iter_markers(name="metadata"), None)
        extended_metadata = next(item.iter_markers(name="extended_metadata"), None)
        if metadata is None:
            missing_metadata.append(item.nodeid)
        else:
            for key in required_metadata_keys:
                if key not in metadata.kwargs:
                    missing_keys.append(f"{item.nodeid}: metadata missing '{key}'")
        if extended_metadata is None:
            missing_metadata.append(item.nodeid)
        else:
            for key in required_extended_keys:
                if key not in extended_metadata.kwargs:
                    missing_keys.append(f"{item.nodeid}: extended_metadata missing '{key}'")

    if missing_metadata or missing_keys:
        message_lines = []
        if missing_metadata:
            message_lines.append("Tests missing required metadata markers:")
            message_lines.extend(missing_metadata)
        if missing_keys:
            message_lines.append("Tests with incomplete metadata fields:")
            message_lines.extend(missing_keys)
        raise pytest.UsageError("\n".join(message_lines))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.passed:
        item._call_passed = True
        item._call_report = rep

    # Only act on failures
    if not rep.failed:
        return

    if rep.when == "teardown" and hasattr(item, "_call_report") and item._call_report.passed:
        item._call_report._count_towards_summary = False
        item._call_report.outcome = "passed"

    if rep.when == "teardown" and hasattr(item, "_call_report") and item._call_report.passed:
        item._call_report._count_towards_summary = False
    elif rep.when != "teardown":
        FAILED_BEFORE_TEARDOWN.add(item.nodeid)

    # If a report already exists for this test and this is not teardown, keep it.
    if getattr(item, "_report_written", False) and rep.when != "teardown":
        return

    steps = get_steps()  # list of (phase_label, message)

    # Parse test class and method
    test_nodeid = item.nodeid
    parts = test_nodeid.split("::")
    test_file = parts[0]
    test_class = parts[1] if len(parts) > 1 else ""
    test_method = parts[2] if len(parts) > 2 else ""

    def extract_failure_reason(msg):
        if "ASSERTION FAILED: " in msg:
            return msg.split("ASSERTION FAILED: ", 1)[1]
        return ""

    # Determine primary failing phase (prefer recorded exceptions)
    recorded_setup = getattr(item, "_setup_exc", None)
    recorded_teardown = getattr(item, "_teardown_exc", None)
    primary_phase = None
    if recorded_setup is not None:
        primary_phase = "setup"
    elif recorded_teardown is not None:
        primary_phase = "teardown"
    else:
        primary_phase = rep.when

    # Group steps by phase
    setup_steps_all = []
    call_steps_all = []
    teardown_steps_all = []
    first_failure = None
    for phase, msg in steps:
        pl = phase.lower()
        if pl.startswith("setup"):
            setup_steps_all.append(msg)
        elif pl.startswith("teardown"):
            teardown_steps_all.append(msg)
        else:
            call_steps_all.append(msg)
        if first_failure is None and "ASSERTION FAILED" in msg:
            first_failure = (pl, msg)

    # Select steps to include based on primary failing phase
    if primary_phase == "setup":
        setup_steps = []
        for m in setup_steps_all:
            setup_steps.append(m)
            if "ASSERTION FAILED" in m:
                break
        call_steps = []
        teardown_steps = []
    elif primary_phase == "call":
        setup_steps = list(setup_steps_all)
        call_steps = []
        for m in call_steps_all:
            call_steps.append(m)
            if "ASSERTION FAILED" in m:
                break
        teardown_steps = []
    else:  # teardown
        setup_steps = list(setup_steps_all)
        call_steps = list(call_steps_all)
        teardown_steps = []
        for m in teardown_steps_all:
            teardown_steps.append(m)
            if "ASSERTION FAILED" in m:
                break

    # Build report text with separate sections
    report_lines = [f"class {test_class}(BaseTest):", f"    RESULT: ERROR", ""]
    if setup_steps:
        report_lines.append("    def setup(self):")
        for s in setup_steps:
            report_lines.append(f"        step(\"{s}\")")
        report_lines.append("")

    report_lines.append(f"    def {test_method}(self):")
    if call_steps:
        for s in call_steps:
            if "ASSERTION FAILED" in s:
                reason = extract_failure_reason(s)
                report_lines.append(f"        assert_step(condition, \"{reason}\")  ---FAILED")
            else:
                report_lines.append(f"        step(\"{s}\")")
    report_lines.append("")

    if teardown_steps:
        report_lines.append("    def teardown(self):")
        for s in teardown_steps:
            if "ASSERTION FAILED" in s:
                reason = extract_failure_reason(s)
                report_lines.append(f"        assert_step(condition, \"{reason}\")  ---FAILED")
            else:
                report_lines.append(f"        step(\"{s}\")")
        report_lines.append("")

    # Append first failure reason if present
    failure_reason = ""
    if first_failure:
        failure_reason = extract_failure_reason(first_failure[1])
    elif hasattr(rep, "longreprtext"):
        failure_reason = rep.longreprtext.splitlines()[0].strip()
    if failure_reason:
        report_lines.append(f"        <Reason of failure: {failure_reason}>")

    report_lines.append("")
    report_content = "\n".join(report_lines)

    # If existing report and this is teardown, append teardown details
    if getattr(item, "_report_written", False) and rep.when == "teardown":
        existing = REPORT_PATH.read_text(encoding="utf-8")
        teardown_steps = [m for p, m in steps if p.lower().startswith("teardown") or p == "Teardown"]
        if teardown_steps:
            teardown_lines = ["", "--- Teardown Failure Details ---"]
            for s in teardown_steps:
                teardown_lines.append(f"    step(\"{s}\")")
            t_reason = ""
            for s in teardown_steps:
                if "ASSERTION FAILED" in s:
                    t_reason = s.split("ASSERTION FAILED: ", 1)[1]
                    break
            if t_reason:
                teardown_lines.append(f"    TEARDOWN FAILED: {t_reason}")
                teardown_lines.append(f"    RESULT: ERROR")
            new_content = existing + "\n" + "\n".join(teardown_lines)
            REPORT_PATH.write_text(new_content, encoding="utf-8")
            if item.nodeid in FAILED_BEFORE_TEARDOWN:
                rep.outcome = "passed"
                rep.longrepr = None
                rep._count_towards_summary = False
            return

    REPORT_PATH.write_text(report_content, encoding="utf-8")
    item._report_written = True
    item._primary_failure_phase = primary_phase

    if rep.when == "teardown" and rep.failed and getattr(item, "_call_passed", False):
        if not hasattr(item.config, "_teardown_failed_nodeids"):
            item.config._teardown_failed_nodeids = set()
        item.config._teardown_failed_nodeids.add(item.nodeid)


def pytest_report_teststatus(report, config):
    if report.when == "teardown" and report.failed:
        if report.nodeid in FAILED_BEFORE_TEARDOWN:
            return None
        return "failed", "F", "TEARDOWN ERROR"


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    passed_reports = terminalreporter.stats.get("passed", [])
    terminalreporter.stats["passed"] = [
        rep
        for rep in passed_reports
        if not (
            rep.when == "call"
            and getattr(rep, "nodeid", None) in FAILED_BEFORE_TEARDOWN
        )
    ]

    failed_reports = terminalreporter.stats.get("failed", [])
    seen = set()
    unique_failed = []
    for rep in failed_reports:
        if rep.nodeid in seen and rep.when != "teardown":
            continue
        seen.add(rep.nodeid)
        unique_failed.append(rep)
    if len(unique_failed) != len(failed_reports):
        terminalreporter.stats["failed"] = unique_failed
