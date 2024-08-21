import logging
import os
import base64

from src.utils import calculate_checksum


def read_and_encode_file(local_path):
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"The file {local_path} does not exist.")
    with open(local_path, 'rb') as file:
        content = file.read()
    return base64.b64encode(content).decode('utf-8')


def compare_checksums(self, local_path, remote_path):
    # Calculate local checksum
    local_checksum = calculate_checksum(local_path)

    # Get remote checksum without passing local_checksum
    remote_checksum = self.get_file_checksum(remote_path)

    # Compare checksums
    if remote_checksum.lower() != local_checksum.lower():
        raise ValueError(f"Checksum mismatch: {local_path} ({local_checksum}) != {remote_path} ({remote_checksum})")

    logging.info("Checksum comparison successful.")
