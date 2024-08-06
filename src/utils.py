import hashlib
import os

from src.ssh_client import SSHClient


def calculate_checksum(file_path):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def delete_remote_script(client, remote_script):
    if isinstance(client, SSHClient):
        delete_command = f"rm -f {remote_script}"
    else:
        delete_command = f"Remove-Item -Path '{remote_script}' -Force"

    output, error = client.execute_command(delete_command)
    print(f"Command used to delete script: {delete_command}")
    print(f"Delete command output: {output}")
    if error:
        print(f"Error deleting remote script {remote_script}: {error}")
    else:
        print(f"Successfully deleted remote script: {remote_script}")


def get_base_dir():
    return os.path.dirname(os.path.abspath(__file__))
