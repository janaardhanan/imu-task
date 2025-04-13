import socket
import time
import argparse
import logging
import struct
import random

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

    try:
        sock= socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        sock.connect(args.socket_path)
    except Exception as e:
        logging.error("Failed to connect to socket: ", e)
        return

    interval = 1.0 / args.frequency_hz
    logging.info("Publisher started")

    try:
        while True:
            data = generate_random_imu_data()
            sock.send(data)
            time.sleep(interval)
    except KeyboardInterrupt:
        logging.info("Publisher exiting")

if __name__ == '__main__':
    main()