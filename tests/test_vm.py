import pytest
from dotenv import load_dotenv
import os
from src.ssh_client import SSHClient
from src.winrm_client import WinRMClient
from src.utils import calculate_checksum

load_dotenv()

@pytest.fixture
def shell_client(request):
    os_option = request.param
    if os_option == 'linux':
        host = os.getenv('LINUX_HOST')
        user = os.getenv('LINUX_USER')
        password = os.getenv('LINUX_PASSWORD')
        return SSHClient(host, user, password)
    elif os_option == 'windows':
        host = os.getenv('WINDOWS_HOST')
        user = os.getenv('WINDOWS_USER')
        password = os.getenv('WINDOWS_PASSWORD')
        return WinRMClient(host, user, password)
    else:
        pytest.fail("Please provide a valid OS option: --os=linux or --os=windows")

@pytest.fixture
def directory(request):
    dirpath = request.config.getoption("--dirpath")
    if not dirpath:
        pytest.fail("Please provide a directory path using --dirpath option.")
    return dirpath

@pytest.mark.parametrize("shell_client", ["linux", "windows"], indirect=True)
def test_create_directory(shell_client, directory, request):
    os_option = 'linux' if isinstance(shell_client, SSHClient) else 'windows'
    os_types = request.config.getoption("--os").split(",")

    if os_option not in os_types:
        pytest.skip(f"Skipping test for OS type {os_option}")

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

    # Upload the script to the remote machine
    shell_client.upload_file(local_script, remote_script)

    # Verify the file was uploaded correctly
    local_checksum = calculate_checksum(local_script)
    print(f"Local checksum: {local_checksum}")

    # Check if remote file is accessible and compute its checksum
    remote_checksum = shell_client.check_file(remote_script, local_checksum)
    print(f"Remote checksum: {remote_checksum}")

    # Normalize both checksums to lowercase before comparison
    assert remote_checksum.lower() == local_checksum.lower(), "Checksum mismatch"

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

    # Clean up: Delete the script file
    if isinstance(shell_client, SSHClient):
        delete_command = f"rm {remote_script}"
    else:
        delete_command = f"Remove-Item -Path {remote_script} -Force"

    shell_client.execute_command(delete_command)
    print(f"Deleted remote script: {remote_script}")

    # Cleanup
    shell_client.close()
