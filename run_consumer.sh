#!/bin/bash

SOCKET_PATH="/tmp/imu_socket"

python3 consumer.py --socket-path "$SOCKET_PATH" --timeout-ms 500 