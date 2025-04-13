import struct
import socket
import argparse
import logging
import os

import numpy as np
from scipy.spatial.transform import Rotation as R

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

def compute_orientation_from_vector(vec):
    vec = np.array(vec)
    if np.linalg.norm(vec) == 0:
        vec = np.array([1.0, 0.0, 0.0])
    vec = vec / np.linalg.norm(vec)
    ref = np.array([0, 0, 1])

    x = np.cross(vec, ref)
    if np.linalg.norm(x) == 0:
        x = np.array([1, 0, 0])
    x /= np.linalg.norm(x)

    y = np.cross(ref, x)
    rot_matrix = np.vstack([x, y, ref]).T

    r = R.from_matrix(rot_matrix)
    return r.as_euler('xyz', degrees=True), r.as_quat()

def log_sensor(name, vector):
    euler, quat = compute_orientation_from_vector(vector)
    logging.info(f"\n**{name.upper()}**")
    logging.info(f"Raw: x={vector[0]:.4f}, y={vector[1]:.4f}, z={vector[2]:.4f}")
    logging.info(f"Euler: Roll={euler[0]:.2f}, Pitch={euler[1]:.2f}, Yaw={euler[2]:.2f}")
    logging.info(f"Quaternion: x={quat[0]:.4f}, y={quat[1]:.4f}, z={quat[2]:.4f}, w={quat[3]:.4f}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--socket-path', required=True)
    parser.add_argument('--timeout-ms', type=int, default=100)
    parser.add_argument('--log-level', default='INFO')
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper()))

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
                if len(data) != 48:
                    logging.warning("Invalid IMU data length")
                    continue

                imu = parse_imu_data(data)
                log_sensor("Accelerometer", imu["acc"])
                log_sensor("Gyroscope", imu["gyro"])
                log_sensor("Magnetometer", imu["mag"])
                logging.info("-" * 40)

            except socket.timeout:
                logging.warning("Timeout waiting for data")
    except KeyboardInterrupt:
        logging.info("Consumer exiting")
    finally:
        sock.close()
        os.remove(args.socket_path)

if __name__ == '__main__':
    main()
