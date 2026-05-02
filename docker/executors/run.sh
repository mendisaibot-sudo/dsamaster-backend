#!/bin/sh
# Generic executor for sandboxed code execution
# Usage: ./run.sh <language> <code_file> <input_file>

LANGUAGE="$1"
CODE_FILE="$2"
INPUT_FILE="$3"

TIMEOUT_SECS=2
MEMORY_LIMIT_MB=128

cd /sandbox || exit 1

case "$LANGUAGE" in
  python)
    # Python execution
    timeout -t "$TIMEOUT_SECS" -m "$MEMORY_LIMIT_MB"000 python3 "$CODE_FILE" < "$INPUT_FILE" 2>&1
    EXIT_CODE=$?
    ;;

  java)
    # Java compilation and execution
    cp "$CODE_FILE" "/sandbox/Main.java"
    javac -encoding UTF-8 "/sandbox/Main.java" 2>&1
    if [ $? -ne 0 ]; then
      exit 1
    fi
    timeout -t "$TIMEOUT_SECS" -m "$MEMORY_LIMIT_MB"000 \
      java -XX:+UseSerialGC -Xmx64m -cp /sandbox Main < "$INPUT_FILE" 2>&1
    EXIT_CODE=$?
    rm -f "/sandbox/Main.java" "/sandbox/Main.class"
    ;;

  cpp)
    # C++ compilation and execution
    BINARY="/sandbox/solution"
    g++ -std=c++17 -O2 -o "$BINARY" "$CODE_FILE" 2>&1
    if [ $? -ne 0 ]; then
      exit 1
    fi
    timeout -t "$TIMEOUT_SECS" -m "$MEMORY_LIMIT_MB"000 "$BINARY" < "$INPUT_FILE" 2>&1
    EXIT_CODE=$?
    rm -f "$BINARY"
    ;;

  *)
    echo "Unsupported language: $LANGUAGE" >&2
    exit 1
    ;;
esac

if [ $EXIT_CODE -eq 124 ] || [ $EXIT_CODE -eq 137 ]; then
  echo "EXECUTION_TIMEOUT" >&2
  exit 124
fi

exit $EXIT_CODE
