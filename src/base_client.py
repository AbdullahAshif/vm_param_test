import hashlib
import os


class BaseShellClient:
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port

    def calculate_checksum(self, file_path, chunk_size=8192):
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as file:
            while chunk := file.read(chunk_size):
                sha256.update(chunk)
        return sha256.hexdigest()

    def get_file_checksum(self, remote_path, expected_checksum):
        raise NotImplementedError("Must be implemented in subclass")

    def upload_file(self, local_path, remote_path):
        raise NotImplementedError("Must be implemented in subclass")

    def execute_command(self, command):
        raise NotImplementedError("Must be implemented in subclass")

    def execute_script(self, local_script, remote_script, directory):
        raise NotImplementedError("Must be implemented in subclass")

    def check_directory_exists(self, directory):
        raise NotImplementedError("Must be implemented in subclass")
