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
    test_suite = ["//tests/sysmon_tests:sysmon_test"],
)
