# tests/test_vm.py
import os
import pytest
from dotenv import load_dotenv
from src.ssh_client import SSHClient
from src.winrm_client import WinRMClient
from src.utils import calculate_checksum

# Load environment variables from .env file
load_dotenv()


@pytest.fixture(params=['linux', 'windows'])
def shell_client(request):
    if request.param == 'linux':
        host = os.getenv('LINUX_HOST')
        user = os.getenv('LINUX_USER')
        password = os.getenv('LINUX_PASSWORD')
        return SSHClient(host, user, password)
    elif request.param == 'windows':
        host = os.getenv('WINDOWS_HOST')
        user = os.getenv('WINDOWS_USER')
        password = os.getenv('WINDOWS_PASSWORD')
        return WinRMClient(host, user, password)


@pytest.fixture
def directory(request):
    dirpath = request.config.getoption("--dirpath")
    if not dirpath:
        pytest.fail("Please provide a directory path using --dirpath option.")
    return dirpath


def test_create_directory(shell_client, directory):
    # Determine the absolute path of the scripts
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if isinstance(shell_client, SSHClient):
        local_script = os.path.join(base_dir, '../scripts/create_dir.sh')
        remote_script = '/tmp/create_dir.sh'
    else:
        local_script = os.path.join(base_dir, '../scripts/create_dir.ps1')
        remote_script = 'C:/Temp/create_dir.ps1'

    # Ensure the script exists before proceeding
    assert os.path.exists(local_script), f"Script {local_script} does not exist."

    shell_client.upload_file(local_script, remote_script)

    # Verify the file was uploaded correctly
    local_checksum = calculate_checksum(local_script)
    print(f"Local checksum: {local_checksum}")

    # Check if remote file is accessible and compute its checksum
    remote_checksum = shell_client.check_file(remote_script, local_checksum)
    print(f"Remote checksum: {remote_checksum}")

    assert remote_checksum, "Checksum mismatch"

    # Execute the file
    if isinstance(shell_client, SSHClient):
        command = f"bash {remote_script} {directory}"
    else:
        command = f"powershell -ExecutionPolicy Bypass -File {remote_script} -dir {directory}"

    shell_client.execute_command(command)

    # Verify the directory was created
    if isinstance(shell_client, SSHClient):
        output = shell_client.execute_command(f"test -d {directory} && echo exists")
        assert "exists" in output, f"Directory {directory} not created"
    else:
        output = shell_client.execute_command(f"if (Test-Path {directory}) {{echo exists}}")
        assert "exists" in output, f"Directory {directory} not created"

    # Cleanup
    shell_client.close()
