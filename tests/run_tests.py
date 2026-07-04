import os
import sys
import pytest

if __name__ == "__main__":
    test_dir = os.path.dirname(os.path.abspath(__file__))
    test_file = os.path.join(test_dir, "test_sysmon.py")
    raise SystemExit(pytest.main([test_file]))
