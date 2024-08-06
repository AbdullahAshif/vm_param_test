import paramiko
import logging


class SSHClient:
    def __init__(self, host, username, password, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.client = None

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

    def get_file_checksum(self, remote_path, local_checksum):
        checksum_command = f"sha256sum {remote_path} | awk '{{print $1}}'"
        remote_checksum, stderr = self.execute_command(checksum_command)
        if stderr:
            logging.error(f"Error getting file checksum: {stderr}")
        if remote_checksum.strip() == local_checksum:
            return remote_checksum.strip()
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()
            logging.info(f"Disconnected from {self.host}.")
