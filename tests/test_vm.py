import pytest
import os

from dotenv import load_dotenv
from src.ssh_client import SSHClient
from src.winrm_client import WinRMClient
from src.utils import calculate_checksum, get_base_dir, delete_remote_script

load_dotenv()


@pytest.fixture
def shell_client(request):
    os_option = request.config.getoption("--os")
    if os_option == 'linux':
        host = os.getenv('LINUX_HOST')
        user = os.getenv('LINUX_USER')
        password = os.getenv('LINUX_PASSWORD')
        with SSHClient(host, user, password) as client:
            yield client
    elif os_option == 'windows':
        host = os.getenv('WINDOWS_HOST')
        user = os.getenv('WINDOWS_USER')
        password = os.getenv('WINDOWS_PASSWORD')
        with WinRMClient(host, user, password) as client:
            yield client
    else:
        pytest.fail("Please provide a valid OS option: --os=linux or --os=windows")


@pytest.mark.parametrize("shell_client", ["linux", "windows"], indirect=True)
@pytest.mark.linux
@pytest.mark.windows
def test_create_directory(shell_client, full_directory_path):
    assert full_directory_path, "No directory path specified"
    base_dir = get_base_dir()

    if isinstance(shell_client, SSHClient):
        local_script = os.path.join(base_dir, '../scripts/create_dir.sh')
        remote_script = '/tmp/create_dir.sh'
    else:
        local_script = os.path.join(base_dir, '../scripts/create_dir.ps1')
        # Use the specified directory path directly
        remote_script = os.path.join(full_directory_path, os.path.basename(local_script))

    assert os.path.exists(local_script), f"Script {local_script} does not exist."

    # Upload the script
    shell_client.upload_file(local_script, remote_script)

    # Verify checksum
    local_checksum = calculate_checksum(local_script)
    print(f"Local checksum: {local_checksum}")
    remote_checksum = shell_client.get_file_checksum(remote_script, local_checksum)
    print(f"Remote checksum: {remote_checksum}")
    assert remote_checksum.lower() == local_checksum.lower(), "Checksum mismatch"

    # Execute the script
    if isinstance(shell_client, SSHClient):
        command = f"bash {remote_script} {full_directory_path}"
    else:
        command = f"powershell -ExecutionPolicy Bypass -File {remote_script} -dir {full_directory_path}"

    print(f"Executing command: {command}")
    output, error = shell_client.execute_command(command)
    print(f"Command output: {output}")
    print(f"Command error: {error}")

    # Check if directory was created
    if isinstance(shell_client, SSHClient):
        check_command = f"test -d {full_directory_path} && echo exists"
    else:
        check_command = f"if (Test-Path '{full_directory_path}') {{echo exists}}"

    check_output, check_error = shell_client.execute_command(check_command)
    print(f"Check command output: {check_output}")
    print(f"Check command error: {check_error}")
    assert "exists" in check_output, f"Directory {full_directory_path} not created"

    # Cleanup
    delete_remote_script(shell_client, remote_script)
