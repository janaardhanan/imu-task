#!/usr/bin/env bash

SOCKET_PATH="/tmp/imu_socket"
TIMEOUT_MS="${1:-500}"
LOG_LEVEL="${2:-info}"

python3 consumer.py \
  --socket-path "$SOCKET_PATH" \
  --timeout-ms "$TIMEOUT_MS" \
  --log-level "$LOG_LEVEL"