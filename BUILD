load("@rules_python//python:defs.bzl", "py_library", "py_test")

py_library(
    name = "framework",
    srcs = glob(["framework/*.py"]),
    imports = ["."],
    deps = [
        "@pip//pytest",
    ],
)

py_test(
    name = "sysmon_test",
    srcs = [
        "tests/run_tests.py",
        "tests/test_sysmon.py",
        "tests/__init__.py",
    ],
    main = "tests/run_tests.py",
    deps = [
        ":framework",
        "@pip//pytest",
    ],
)