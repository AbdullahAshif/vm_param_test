import paramiko
import logging

from src.base_client import BaseShellClient
from src.utils import calculate_checksum


class SSHClient(BaseShellClient):
    def __enter__(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host, port=self.port, username=self.username, password=self.password)
            logging.info(f"Connected to {self.host} successfully.")
        except Exception as e:
            logging.error(f"Failed to connect to {self.host}: {e}")
            self.client = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()
            logging.info(f"Disconnected from {self.host}.")

    def execute_command(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        output = stdout.read().decode('utf-8').strip()
        error = stderr.read().decode('utf-8').strip()
        if error:
            raise RuntimeError(f"Command execution failed: {error}")

        return output

    def upload_file(self, local_path, remote_path):
        if self.client is None:
            raise ConnectionError("SSH connection not established.")
        try:
            sftp = self.client.open_sftp()
            sftp.put(local_path, remote_path)
            sftp.close()
            logging.info(f"Uploaded {local_path} to {remote_path} successfully.")
        except Exception as e:
            logging.error(f"Failed to upload file: {e}")

    def execute_script(self, remote_script, directory):
        # Execute the script
        command = f"bash {remote_script} {directory}"
        output = self.execute_command(command)
        return output

    def check_directory_exists(self, directory):
        check_command = f"test -d {directory} && echo exists"
        check_output = self.execute_command(check_command)
        return "exists" in check_output

    def get_file_checksum(self, remote_path):
        checksum_command = f"sha256sum {remote_path}"
        checksum_output = self.execute_command(checksum_command)
        checksum = checksum_output.split()[0].strip()
        return checksum

    def delete_file(self, remote_path):
        delete_command = f"rm -f {remote_path}"
        self.execute_command(delete_command)
        print(f"Successfully deleted remote script: {remote_path}")
