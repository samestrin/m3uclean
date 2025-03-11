#!/bin/bash

# Default values 
INPUT_FILE="playlist.m3u"
OUTPUT_FILE=""
LOG_FILE=""
STREAM_VALIDATE="false"
AGGRESSIVE_CLEAN="false"
DOCKER_IMAGE="m3uclean"
MOUNT_DIR="$(pwd)"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--input)
      INPUT_FILE="$2"
      shift 2
      ;;
    -o|--output)
      OUTPUT_FILE="$2"
      shift 2
      ;;
    -l|--log)
      LOG_FILE="$2"
      shift 2
      ;;
    -v|--validate)
      STREAM_VALIDATE="true"
      shift
      ;;
    -a|--aggressive)
      AGGRESSIVE_CLEAN="true"
      shift
      ;;
    -d|--directory)
      MOUNT_DIR="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Set default output file if not specified
if [ -z "$OUTPUT_FILE" ]; then
  OUTPUT_FILE="${INPUT_FILE%.*}_clean.m3u"
fi

# Set default log file if not specified
if [ -z "$LOG_FILE" ]; then
  LOG_FILE="${INPUT_FILE%.*}.log"
fi

# Get absolute paths
MOUNT_DIR=$(realpath "$MOUNT_DIR")
REL_INPUT=$(realpath --relative-to="$MOUNT_DIR" "$(realpath "$INPUT_FILE")")
REL_OUTPUT=$(realpath --relative-to="$MOUNT_DIR" "$(realpath "$OUTPUT_FILE")")
REL_LOG=$(realpath --relative-to="$MOUNT_DIR" "$(realpath "$LOG_FILE")")

# Run the Docker container
echo "Running m3uclean with:"
echo "  Input file: $INPUT_FILE"
echo "  Output file: $OUTPUT_FILE"
echo "  Log file: $LOG_FILE"
echo "  Stream validation: $STREAM_VALIDATE"
echo "  Aggressive cleaning: $AGGRESSIVE_CLEAN"
echo "  Mount directory: $MOUNT_DIR"

docker run -it --rm \
  -e INPUT_FILE="/var/tmp/m3u/$REL_INPUT" \
  -e OUTPUT_FILE="/var/tmp/m3u/$REL_OUTPUT" \
  -e LOG_FILE="/var/tmp/m3u/$REL_LOG" \
  -e STREAM_VALIDATE="$STREAM_VALIDATE" \
  -e AGGRESSIVE_CLEAN="$AGGRESSIVE_CLEAN" \
  -v "$MOUNT_DIR:/var/tmp/m3u" \
  "$DOCKER_IMAGE"

echo "Done."
