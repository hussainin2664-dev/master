load("@rules_python//python:defs.bzl", "py_test")

def _sorted_labels(labels):
    # Return a sorted copy of the list of labels (string order)
    return sorted(labels)


def py_inamdar_test(name, test_suite, deps = []):
    """
    Macro wrapper that enforces alphabetical order on `test_suite` labels
    and creates a `test_suite` target.

    Usage in BUILD:
      load("//:py_inamdar.bzl", "py_inamdar_test")
      py_inamdar_test(
          name = "main_test_target",
          test_suite = ["//tests/sysmon_tests:sysmon_test"],
      )
    """
    sorted_list = _sorted_labels(test_suite)
    if test_suite != sorted_list:
        fail("py_inamdar_test: `test_suite` entries must be in alphabetical order.\n" +
             "Expected order: %s\nCurrent order: %s" % (sorted_list, test_suite))

    native.test_suite(name = name, tests = test_suite)


def py_inamdar_py_test(name, srcs, main = None, deps = [], visibility = None):
    """
    Wrapper around `py_test` that enforces alphabetical ordering of `srcs`.
    """
    sorted_srcs = sorted(srcs)
    if srcs != sorted_srcs:
        fail("py_inamdar_py_test: `srcs` entries must be in alphabetical order.\n" +
             "Expected order: %s\nCurrent order: %s" % (sorted_srcs, srcs))

    py_test(name = name, srcs = srcs, main = main, deps = deps, visibility = visibility)
