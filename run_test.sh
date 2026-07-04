#!/bin/bash

OUTPUT_DIR="output"
PYTHON_EXE="./.venv/Scripts/python.exe"
DEFAULT_TEST_FILE="tests/test_sysmon.py"
TEST_FILE="${1:-$DEFAULT_TEST_FILE}"

mkdir -p "$OUTPUT_DIR"
find "$OUTPUT_DIR" -maxdepth 1 -type f ! -name 'test.log' ! -name 'report.xml' -delete
rm -f "$OUTPUT_DIR/test.log" "$OUTPUT_DIR/report.xml"

printf '' > "$OUTPUT_DIR/report.xml"

echo "======================================"
echo "Running pytest: $TEST_FILE"
echo "======================================"

set +e
"$PYTHON_EXE" -m pytest -q "$TEST_FILE"
STATUS=$?
set -e

if [ -f "$OUTPUT_DIR/report.xml" ]; then
    echo ""
    echo "--- report.xml ---"
    cat "$OUTPUT_DIR/report.xml"
fi

exit $STATUS
