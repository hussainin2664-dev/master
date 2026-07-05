#!/bin/bash

OUTPUT_DIR="output"
PYTHON_EXE="./.venv/Scripts/python.exe"
RUNNER="tests/monitor_tests/run_tests.py"
DEFAULT_TEST_TARGET="tests/monitor_tests"

if [ "$#" -gt 0 ]; then
    TEST_TARGETS=("$@")
else
    TEST_TARGETS=("$DEFAULT_TEST_TARGET")
fi

mkdir -p "$OUTPUT_DIR"
find "$OUTPUT_DIR" -maxdepth 1 -type f ! -name 'test.log' ! -name 'report.xml' -delete
rm -f "$OUTPUT_DIR/test.log" "$OUTPUT_DIR/report.xml"

printf '' > "$OUTPUT_DIR/report.xml"

echo "======================================"
echo "Running custom test runner: $RUNNER ${TEST_TARGETS[*]}"
echo "======================================"

set +e
"$PYTHON_EXE" "$RUNNER" "${TEST_TARGETS[@]}"
STATUS=$?
set -e

if [ -f "$OUTPUT_DIR/report.xml" ]; then
    echo ""
    echo "--- report.xml ---"
    cat "$OUTPUT_DIR/report.xml"
    echo ""
fi

echo ""
exit $STATUS
