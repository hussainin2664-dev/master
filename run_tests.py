import os
import sys
import pytest

if __name__ == "__main__":
    repo_root = os.path.dirname(os.path.abspath(__file__))
    default_test_target = os.path.join(repo_root, "tests", "monitor_tests")
    args = sys.argv[1:] or [default_test_target]
    raise SystemExit(pytest.main(args))
