import hashlib
import os


class BaseShellClient:
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port

    def get_file_checksum(self, remote_path, expected_checksum):
        raise NotImplementedError("Must be implemented in subclass")

    def upload_file(self, local_path, remote_path):
        raise NotImplementedError("Must be implemented in subclass")

    def execute_command(self, command):
        raise NotImplementedError("Must be implemented in subclass")

    def execute_script(self, remote_script, directory):
        raise NotImplementedError("Must be implemented in subclass")

    def compare_checksums(self, local_path, remote_path):
        """Compare checksums of the local and remote files."""
        raise NotImplementedError("Must be implemented in subclass")

    def check_directory_exists(self, directory):
        raise NotImplementedError("Must be implemented in subclass")

    def run_script(self, local_script, remote_script, directory):
        """Upload the script, compare checksums, and execute the script."""
        # Upload the script
        self.upload_file(local_script, remote_script)

        # Compare checksums
        self.compare_checksums(local_script, remote_script)

        # Execute the script
        output = self.execute_script(remote_script, directory)
        return output
