import os
import platform
import subprocess
import sys

from framework.utils import is_process_running


def launch_application():
    # Placeholder for application startup logic.
    # If the test environment requires a real application, implement startup here.
    return True


def close_application():
    # Placeholder for application shutdown logic.
    # If the test environment requires a real application, implement shutdown here.
    return True


def verify_python_process_is_running():
    executable = os.path.basename(sys.executable)
    return is_process_running(executable)


def verify_monitor_rules_loaded():
    if platform.system() != "Windows":
        return False

    try:
        result = subprocess.run(
            ["sc", "query", "monitor"],
            capture_output=True,
            text=True,
        )
        output = result.stdout.lower()
        return "service_name" in output and "monitor" in output and "running" in output
    except Exception:
        return False


def verify_monitor_event_collection():
    if platform.system() != "Windows":
        return False

    try:
        result = subprocess.run(
            [
                "wevtutil",
                "qe",
                "Microsoft-Windows-Monitor/Operational",
                "/c:1",
                "/f:text",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )
        return result.returncode == 0 and bool(result.stdout.strip())
    except Exception:
        return False
