load("//:py_inamdar.bzl", "py_inamdar_py_test")

py_inamdar_py_test(
    name = "monitor_test",
    srcs = [
        "__init__.py",
        "conftest.py",
        "helpers.py",
        "run_tests.py",
        "test_monitor.py",
        "test_python_application.py",
    ],
    main = "run_tests.py",
    deps = [
        "//:framework",
        "//tests:tests_pkg",
        "@pip//pytest",
    ],
    size = "small",
    visibility = ["//visibility:public"],
)
