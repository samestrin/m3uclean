#!/bin/bash
set -e

# Execute m3uclean with environment variables
exec python -m m3uclean.app "$INPUT_FILE" -o "$OUTPUT_FILE" -l "$LOG_FILE" \
  $([ "$STREAM_VALIDATE" = "true" ] && echo "-v") \
  $([ "$AGGRESSIVE_CLEAN" = "true" ] && echo "-a")