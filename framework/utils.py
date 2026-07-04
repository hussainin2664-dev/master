import platform
import shutil
import subprocess


def _is_process_running_unix(process):
    if shutil.which("pgrep"):
        result = subprocess.run(
            ["pgrep", process],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0

    result = subprocess.run(
        ["ps", "-A"],
        capture_output=True,
        text=True,
    )
    return process in result.stdout


def is_process_running(process):
    if platform.system() == "Windows":
        process_name = process if process.lower().endswith(".exe") else f"{process}.exe"
        result = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {process_name}", "/NH"],
            capture_output=True,
            text=True,
        )
        output = result.stdout.strip()
        if not output or "no tasks are running" in output.lower():
            return False
        return process_name.lower() in output.lower()

    return _is_process_running_unix(process)
