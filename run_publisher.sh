#!/usr/bin/env bash

SOCKET_PATH="${1:-/tmp/imu_socket}"
FREQ="${2:-10}"
TYPE="${3:-random}"
LOG_LEVEL="${4:-info}"

python3 publisher.py \
  --socket-path "$SOCKET_PATH" \
  --frequency-hz "$FREQ" \
  --publishing-type "$TYPE" \
  --log-level "$LOG_LEVEL"