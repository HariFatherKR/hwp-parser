#!/bin/bash
# HWP to various formats converter
# Usage: ./convert.sh <input.hwp> <format> [output_path]

set -e

INPUT="$1"
FORMAT="${2:-text}"
OUTPUT="$3"

if [ -z "$INPUT" ]; then
    echo "Usage: $0 <input.hwp> [format] [output]"
    echo "Formats: text, html, odt, pdf"
    exit 1
fi

# Activate venv if exists
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_PATH="${SCRIPT_DIR}/../../../venv"

if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
fi

# Run conversion
if [ -z "$OUTPUT" ]; then
    hwpparser convert "$INPUT" -f "$FORMAT"
else
    hwpparser convert "$INPUT" -f "$FORMAT" -o "$OUTPUT"
fi
