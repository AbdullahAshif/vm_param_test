# src/utils/file_utils.py

import os
import base64


def read_and_encode_file(local_path):
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"The file {local_path} does not exist.")
    with open(local_path, 'rb') as file:
        content = file.read()
    return base64.b64encode(content).decode('utf-8')
