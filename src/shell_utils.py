# src/shell_utils.py
import os
from src.ssh_client import SSHClient
from src.winrm_client import WinRMClient


def get_script_paths(shell_client, base_dir, full_directory_path):
    if isinstance(shell_client, SSHClient):
        local_script = os.path.join(base_dir, '../scripts/create_dir.sh')
        remote_script = '/tmp/create_dir.sh'
    elif isinstance(shell_client, WinRMClient):
        local_script = os.path.join(base_dir, '../scripts/create_dir.ps1')
        remote_script = os.path.join(full_directory_path, os.path.basename(local_script))
    else:
        raise ValueError("Unsupported shell client type")
    return local_script, remote_script
