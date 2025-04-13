#!/bin/bash

SOCKET_PATH="/tmp/imu_socket"

python3 publisher.py --socket-path "$SOCKET_PATH" --frequency-hz 10