import struct
import socket
import argparse
import logging
import os

IMU_STRUCT = struct.Struct("<3fI3iI3fI")

def parse_imu_data(data):
    unpacked = IMU_STRUCT.unpack(data)
    return {
        'acc': unpacked[0:3],
        'ts_acc': unpacked[3],
        'gyro': unpacked[4:7],
        'ts_gyro': unpacked[7],
        'mag': unpacked[8:11],
        'ts_mag': unpacked[11],
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--socket-path', required=True)
    parser.add_argument('--timeout-ms', type=int, default=100)
    parser.add_argument('--log-level', default='INFO')
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

    # Ensure old socket doesn't block
    if os.path.exists(args.socket_path):
        os.remove(args.socket_path)

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.bind(args.socket_path)
    sock.settimeout(args.timeout_ms / 1000.0)

    logging.info("Consumer started")

    try:
        while True:
            try:
                data = sock.recv(48)
                imu = parse_imu_data(data)
                logging.info(f"Received IMU: {imu}")
            except socket.timeout:
                logging.warning("Timeout waiting for data")
    except KeyboardInterrupt:
        logging.info("Consumer exiting")
    finally:
        sock.close()
        os.remove(args.socket_path)

if __name__ == '__main__':
    main()
