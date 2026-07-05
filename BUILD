load("@rules_python//python:defs.bzl", "py_library")
load("//:py_inamdar.bzl", "py_inamdar_test")

py_library(
    name = "framework",
    srcs = glob(["framework/*.py"]),
    imports = ["."],
    deps = [
        "@pip//pytest",
    ],
    visibility = ["//visibility:public"],
)

py_inamdar_test(
    name = "main_test_target",
    test_suite = ["//tests/monitor_tests:monitor_test"],
)
