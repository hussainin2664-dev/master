load("//:py_inamdar.bzl", "py_inamdar_py_test")

py_inamdar_py_test(
    name = "sysmon_test",
    srcs = [
        "__init__.py",
        "conftest.py",
        "run_tests.py",
        "test_dummy.py",
        "test_sysmon.py",
    ],
    main = "run_tests.py",
    deps = [
        "//:framework",
        "@pip//pytest",
    ],
    visibility = ["//visibility:public"],
)
