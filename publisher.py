import socket
import time
import argparse
import logging
import struct
import random
import os
import math

IMU_STRUCT = struct.Struct("<3fI3iI3fI")

def generate_imu_data(mode):
    now = time.time()
    ts = int(now)
    angle = math.sin(now)  # Smooth oscillation [-1, 1]

    if mode == 'random':
        xAcc, yAcc, zAcc = [random.uniform(-2.0, 2.0) for _ in range(3)]
        xGyro, yGyro, zGyro = [random.randint(-50000, 50000) for _ in range(3)]
        xMag, yMag, zMag = [random.uniform(-100.0, 100.0) for _ in range(3)]
    elif mode == 'yaw':
        xAcc, yAcc, zAcc = 0.0, 0.0, 9.81  # no tilt
        xGyro, yGyro, zGyro = 0, 0, int(angle * 50000) 
        xMag = 50 * math.cos(now)
        yMag = 50 * math.sin(now)
        zMag = 0.0
    elif mode == 'pitch':
        xAcc = 9.81 * math.sin(angle)
        yAcc = 0.0
        zAcc = 9.81 * math.cos(angle)
        xGyro, yGyro, zGyro = 0, int(angle * 50000), 0  # rotate around Y
        xMag, yMag, zMag = 30.0, 0.0, 40.0
    elif mode == 'roll':
        xAcc = 0.0
        yAcc = 9.81 * math.sin(angle)
        zAcc = 9.81 * math.cos(angle)
        xGyro, yGyro, zGyro = int(angle * 50000), 0, 0  # rotate around X
        xMag, yMag, zMag = 30.0, 0.0, 40.0
    else:
        raise ValueError("Invalid publishing type. Choose from: random, yaw, pitch, roll")

    return IMU_STRUCT.pack(
        xAcc, yAcc, zAcc, ts,
        xGyro, yGyro, zGyro, ts,
        xMag, yMag, zMag, ts
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--socket-path', required=True)
    parser.add_argument('--frequency-hz', type=int, default=10)
    parser.add_argument('--publishing-type', choices=['random', 'yaw', 'pitch', 'roll'], default='random')
    parser.add_argument('--log-level', default='INFO')
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    while True:
        if not os.path.exists(args.socket_path):
            logging.warning("Socket not available. Retrying...")
            time.sleep(1)
            continue

        interval = 1.0 / args.frequency_hz
        logging.info(f"Publisher started with mode '{args.publishing_type}'")

        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            sock.connect(args.socket_path)
            logging.info("Publisher connected")

            while True:
                data = generate_imu_data(args.publishing_type)
                sock.send(data)
                time.sleep(interval)
        except (FileNotFoundError, ConnectionRefusedError, OSError) as e:
            logging.warning(f"Connection lost: {e}. Reconnecting...")
            sock.close()
            time.sleep(1)
        except KeyboardInterrupt:
            logging.info("Publisher interrupted, exiting.")
            break

if __name__ == '__main__':
    main()