import base64
import logging
import os
import winrm
from src.base_client import BaseShellClient
from scripts.powershell_scripts import (
    create_directory_script,
    upload_file_script,
    file_exists_check_script,
    get_file_checksum_script
)
from src.utils import calculate_checksum
from utils.assertions import assert_equal_ignore_case


class WinRMClient(BaseShellClient):
    def __init__(self, host, username, password):
        super().__init__(host, username, password)
        self.session = (winrm.Session
                        (host, auth=(username, password), transport='basic', server_cert_validation='ignore'))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        logging.info(f"Disconnected from {self.host}.")
        pass

    @staticmethod
    def read_and_encode_file(local_path):
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"The file {local_path} does not exist.")
        with open(local_path, 'rb') as file:
            content = file.read()
        return base64.b64encode(content).decode('utf-8')

    def create_remote_directory(self, directory):
        create_dir_script = create_directory_script(directory)
        result = self.session.run_ps(create_dir_script)
        if result.std_err:
            raise RuntimeError(f"Error creating directory: {result.std_err.decode().strip()}")

    def check_remote_directory_exists(self, directory):
        dir_exists_script = file_exists_check_script(directory)
        result = self.session.run_ps(dir_exists_script)
        if result.std_err:
            raise RuntimeError(f"Error checking directory: {result.std_err.decode().strip()}")
        return result.std_out.decode().strip().lower() == 'true'

    def upload_file_content(self, encoded_content, remote_path):
        upload_script = upload_file_script(encoded_content, remote_path)
        result = self.session.run_ps(upload_script)
        if result.std_err:
            raise RuntimeError(f"Error uploading file: {result.std_err.decode().strip()}")
        if not self.check_remote_directory_exists(remote_path):
            raise FileNotFoundError(f"File {remote_path} does not exist after upload.")

    def upload_file(self, local_path, remote_path):
        encoded_content = self.read_and_encode_file(local_path)
        directory = os.path.dirname(remote_path)
        self.create_remote_directory(directory)
        if not self.check_remote_directory_exists(directory):
            raise FileNotFoundError(f"Directory {directory} does not exist after creation.")
        self.upload_file_content(encoded_content, remote_path)

    def execute_command(self, command):
        print(f"Executing command: {command}")
        result = self.session.run_ps(command)
        output = result.std_out.decode().strip()
        error = result.std_err.decode().strip()
        print(f"Command output: {output}")
        if error:
            print(f"Command error: {error}")
        return output, error

    def get_file_checksum(self, remote_path):
        checksum_script = get_file_checksum_script(remote_path)
        result = self.session.run_ps(checksum_script)
        if result.std_err:
            raise RuntimeError(f"Error retrieving checksum: {result.std_err.decode().strip()}")
        return result.std_out.decode().strip()

    def execute_script(self, remote_script, directory):
        command = f"powershell -ExecutionPolicy Bypass -File {remote_script} -dir {directory}"
        output, error = self.execute_command(command)
        if error:
            raise RuntimeError(f"Script execution failed: {error}")
        return output

    def check_directory_exists(self, directory):
        check_command = f"if (Test-Path '{directory}') {{echo exists}}"
        check_output, check_error = self.execute_command(check_command)
        if check_error:
            raise RuntimeError(f"Directory check failed: {check_error}")
        return "exists" in check_output

    def delete_file(self, remote_path):
        delete_command = f"Remove-Item -Path '{remote_path}' -Force"
        output, error = self.execute_command(delete_command)
        if error:
            raise RuntimeError(f"Failed to delete remote file: {error}")
        print(f"Successfully deleted remote script: {remote_path}")
