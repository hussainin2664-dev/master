import os
import sys
import re
import pytest
import xml.etree.ElementTree as ET
from datetime import datetime


def _write_test_log(workspace_root, junit_path):
    test_log_path = os.path.join(workspace_root, "output", "test.log")
    try:
        tree = ET.parse(junit_path)
        root = tree.getroot()
        suites = []
        if root.tag == "testsuites":
            suites = root.findall("testsuite")
        elif root.tag == "testsuite":
            suites = [root]

        total = failed = skipped = 0
        test_names = []
        for s in suites:
            total += int(s.attrib.get("tests", "0"))
            failed += int(s.attrib.get("failures", "0")) + int(s.attrib.get("errors", "0"))
            skipped += int(s.attrib.get("skipped", "0"))
            for tc in s.findall("testcase"):
                cls = tc.attrib.get("classname", "")
                name = tc.attrib.get("name", "")
                test_names.append((cls + "::" + name).lstrip("::"))

        passed = total - failed - skipped
        os.makedirs(os.path.join(workspace_root, "output"), exist_ok=True)
        # Append summary to existing test.log (keep detailed logs already present)
        with open(test_log_path, "a", encoding="utf-8") as fh:
            fh.write("\n--- Test Summary ---\n")
            fh.write(f"Total: {total}\n")
            fh.write(f"Passed: {passed}\n")
            fh.write(f"Failed: {failed}\n")
            fh.write(f"Skipped: {skipped}\n\n")
            fh.write("Executed tests:\n")
            for n in test_names:
                fh.write(n + "\n")
    except Exception:
        # Leave detailed logs intact; append a fallback message
        os.makedirs(os.path.join(workspace_root, "output"), exist_ok=True)
        with open(test_log_path, "a", encoding="utf-8") as fh:
            fh.write("\n--- Test Summary ---\nCould not parse junit xml.\n")


if __name__ == "__main__":
    pkg_dir = os.path.dirname(os.path.abspath(__file__))
    workspace_root = os.path.abspath(os.path.join(pkg_dir, "..", ".."))
    sys.path.insert(0, workspace_root)
    default_test_target = pkg_dir
    args = sys.argv[1:] or [default_test_target]

    # Prefer Bazel test outputs dir when available so files are preserved by Bazel test runner
    bazel_output_dir = os.environ.get("TEST_UNDECLARED_OUTPUTS_DIR") or os.environ.get("TEST_TMPDIR")
    workspace_output_dir = os.path.join(workspace_root, "output")
    output_dir = bazel_output_dir or workspace_output_dir
    output_dirs = [output_dir]
    if bazel_output_dir and bazel_output_dir != workspace_output_dir:
        output_dirs.append(workspace_output_dir)

    for d in output_dirs:
        os.makedirs(d, exist_ok=True)
    # Clear custom report file before the run so stale XML does not remain
    report_file_path = os.path.join(output_dir, "report.xml")
    with open(report_file_path, "w", encoding="utf-8"):
        pass
    # Ensure pytest junit xml is generated to a separate file so custom report.xml remains available
    junit_path = os.path.join(output_dir, "pytest_report.xml")
    if not any(arg.startswith("--junitxml") for arg in args):
        args = args + ["--junitxml=" + junit_path]

    # Prepare/clear test log so we stream per-test entries
    test_log_path = os.path.join(output_dir, "test.log")
    # truncate log for this run
    with open(test_log_path, "w", encoding="utf-8"):
        pass

    # Collect results via a small pytest plugin so we can always write a summary
    class _ResultCollector:
        def __init__(self):
            # map nodeid -> dict of flags
            self._results = {}
            # cumulative counters
            self.count_passed = 0
            self.count_failed = 0
            self.count_error = 0
            self.count_skipped = 0

        def pytest_runtest_logreport(self, report):
            node = report.nodeid
            entry = self._results.setdefault(node, {"passed": False, "failed": False, "skipped": False, "failed_phase": None, "order_written": False})
            if getattr(report, "skipped", False):
                entry["skipped"] = True
            if getattr(report, "failed", False):
                entry["failed"] = True
                entry["failed_phase"] = report.when
            # mark passed only for the call phase
            if report.when == "call" and getattr(report, "passed", False):
                entry["passed"] = True
            # When teardown finishes, write header + captured output + result status
            if report.when == "teardown" and not entry.get("order_written", False):
                # determine final status
                if entry.get("skipped"):
                    status = "SKIPPED"
                    self.count_skipped += 1
                elif entry.get("failed"):
                    phase = entry.get("failed_phase")
                    if phase == "call":
                        status = "FAILED"
                        self.count_failed += 1
                    else:
                        status = "ERROR"
                        self.count_error += 1
                elif entry.get("passed"):
                    status = "PASSED"
                    self.count_passed += 1
                else:
                    status = "PASSED"
                    self.count_passed += 1

                # store captured output and timestamp for post-run write
                out = getattr(report, "capstdout", "") or ""
                sections = []
                for section in getattr(report, "sections", []):
                    try:
                        sections.append(section[1])
                    except Exception:
                        pass

                entry["captured"] = out + ("\n".join(sections) if sections else "")
                entry["ts"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                entry["status"] = status
                entry["order_written"] = True

        @property
        def tests(self):
            return list(self._results.keys())

        @property
        def passed(self):
            return sum(1 for v in self._results.values() if (not v["failed"] and not v["skipped"]))

        @property
        def failed(self):
            # count failures that occurred during the call phase
            return sum(1 for v in self._results.values() if v.get("failed") and v.get("failed_phase") == "call")

        @property
        def skipped(self):
            return sum(1 for v in self._results.values() if v["skipped"] and not v["failed"]) 

    collector = _ResultCollector()
    exit_code = pytest.main(args, plugins=[collector])

    # append a summary using collected results
    os.makedirs(output_dir, exist_ok=True)
    test_log_path = os.path.join(output_dir, "test.log")

    def _format_test_capture(raw_capture, ts):
        ANSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
        clean_capture = ANSI_RE.sub("", raw_capture or "")
        lines = []
        seen = set()
        for raw_line in clean_capture.splitlines():
            line = raw_line.strip()
            if not line:
                if lines and lines[-1] != "":
                    lines.append("")
                continue
            if line in seen:
                continue
            seen.add(line)
            if line.startswith("[STEP") or line.startswith("STEP"):
                lines.append(f"{ts} {line}")
            elif line.startswith("INFO") or line.startswith("DEBUG") or line.startswith("WARNING") or line.startswith("ERROR"):
                # omit logger output to keep report clean and avoid duplicates
                continue
            else:
                lines.append(line)
        return lines

    try:
        with open(test_log_path, "w", encoding="utf-8") as fh:
            for idx, n in enumerate(collector.tests):
                e = collector._results.get(n, {})
                ts = e.get("ts") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                parts = n.split("::")
                file_path = parts[0].replace("\\", "/")
                abs_file_path = os.path.abspath(os.path.join(workspace_root, file_path))
                test_id = "::".join(parts[1:]) if len(parts) > 1 else ""
                display_test = f"{abs_file_path}::{test_id}" if test_id else abs_file_path

                if idx > 0:
                    fh.write("\n")

                fh.write(f"{ts} Executing test {display_test}\n")
                cap = e.get("captured") or ""
                if cap:
                    formatted_lines = _format_test_capture(cap, ts)
                    if formatted_lines:
                        fh.write("\n".join(formatted_lines))
                        fh.write("\n")

                status = e.get("status") or ("PASSED" if e.get("passed") else "")
                fh.write(f"{display_test}: {status}\n\n")

            # final summary
            fh.write("--- Overall Test Summary ---\n")
            fh.write(f"Total: {len(collector.tests)}\n")
            fh.write(f"Passed: {collector.passed}\n")
            fh.write(f"Failed: {collector.failed}\n")
            fh.write(f"Error: {collector.count_error if hasattr(collector, 'count_error') else 0}\n")
            fh.write(f"Skipped: {collector.skipped}\n\n")
            fh.write("Executed tests:\n")
            for n in collector.tests:
                e = collector._results.get(n, {})
                parts = n.split("::")
                file_path = parts[0].replace("\\", "/")
                abs_file_path = os.path.abspath(os.path.join(workspace_root, file_path))
                test_id = "::".join(parts[1:]) if len(parts) > 1 else ""
                display_test = f"{abs_file_path}::{test_id}" if test_id else abs_file_path

                if e.get("skipped"):
                    st = "SKIPPED"
                elif e.get("failed"):
                    ph = e.get("failed_phase")
                    st = "FAILED" if ph == "call" else "ERROR"
                elif e.get("passed"):
                    st = "PASSED"
                else:
                    st = "PASSED"
                fh.write(f"{display_test} {st}\n")
    except Exception:
        pass

    # Copy Bazel output files back to workspace output dir when running under Bazel
    if bazel_output_dir and bazel_output_dir != workspace_output_dir:
        try:
            import shutil

            shutil.copyfile(os.path.join(output_dir, "test.log"), os.path.join(workspace_output_dir, "test.log"))
            shutil.copyfile(os.path.join(output_dir, "report.xml"), os.path.join(workspace_output_dir, "report.xml"))
        except Exception:
            pass

    # (Don't duplicate JUnit parsing here; collector already wrote a concise summary.)
    raise SystemExit(exit_code)
