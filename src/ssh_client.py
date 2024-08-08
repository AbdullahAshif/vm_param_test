import paramiko
import logging

from src.base_client import BaseShellClient


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

    def execute_command(self, command):
        if self.client is None:
            raise ConnectionError("SSH connection not established.")
        try:
            stdin, stdout, stderr = self.client.exec_command(command)
            return stdout.read().decode('utf-8'), stderr.read().decode('utf-8')
        except Exception as e:
            logging.error(f"Failed to execute command: {e}")
            return "", str(e)

    def execute_script(self, local_script, remote_script, directory):
        # Upload the script
        self.upload_file(local_script, remote_script)

        # Verify checksum
        local_checksum = self.calculate_checksum(local_script)
        remote_checksum = self.get_file_checksum(remote_script, local_checksum)
        if remote_checksum.lower() != local_checksum.lower():
            raise ValueError("Checksum mismatch")

        # Execute the script
        command = f"bash {remote_script} {directory}"
        output, error = self.execute_command(command)
        if error:
            raise RuntimeError(f"Script execution failed: {error}")
        return output

    def check_directory_exists(self, directory):
        check_command = f"test -d {directory} && echo exists"
        check_output, check_error = self.execute_command(check_command)
        if check_error:
            raise RuntimeError(f"Directory check failed: {check_error}")
        return "exists" in check_output

    def get_file_checksum(self, remote_path, expected_checksum):
        checksum_command = f"sha256sum {remote_path}"
        checksum_output, checksum_error = self.execute_command(checksum_command)
        if checksum_error:
            raise RuntimeError(f"Checksum retrieval failed: {checksum_error}")
        checksum = checksum_output.split()[0].strip()
        if checksum.lower() != expected_checksum.lower():
            raise ValueError(f"Checksum mismatch. Expected: {expected_checksum}, Got: {checksum}")
        return checksum

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()
            logging.info(f"Disconnected from {self.host}.")
