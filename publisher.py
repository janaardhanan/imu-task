import socket
import time
import argparse
import logging
import struct
import random
import os

IMU_STRUCT = struct.Struct("<3fI3iI3fI")

def generate_random_imu_data():
    # Generate fake sensor data
    xAcc, yAcc, zAcc = [random.uniform(-2.0, 2.0) for _ in range(3)]
    xGyro, yGyro, zGyro = [random.randint(-50000, 50000) for _ in range(3)]
    xMag, yMag, zMag = [random.uniform(-100.0, 100.0) for _ in range(3)]
    ts = int(time.time())

    imu_structure=IMU_STRUCT.pack(xAcc, yAcc, zAcc, ts,
                              xGyro, yGyro, zGyro, ts,
                              xMag, yMag, zMag, ts)
    
    return imu_structure

def main():
    parser= argparse.ArgumentParser()
    parser.add_argument('--socket-path', required=True)
    parser.add_argument('--frequency-hz', type=int, default=10)
    parser.add_argument('--log-level', default='INFO')
    args=parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    while True:
        if not os.path.exists(args.socket_path):
            logging.warning("Socket not available. Retrying...")
            time.sleep(1)
            continue
        interval = 1.0 / args.frequency_hz
        logging.info("Publisher started")

        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
            sock.connect(args.socket_path)
            logging.info("Publisher connected")

            while True:
                data = generate_random_imu_data()
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