import pytest
import os
from dotenv import load_dotenv
from src.ssh_client import SSHClient
from src.winrm_client import WinRMClient
from src.utils import get_base_dir, get_env_var, calculate_checksum
from src.shell_utils import get_script_paths, delete_remote_script
from src.constants import OSType
from utils.assertions import assert_equal_ignore_case
from typing import Union

load_dotenv()


@pytest.fixture
def shell_client(request) -> Union[SSHClient, WinRMClient]:
    os_option_str = request.config.getoption("--os").lower()

    os_option_mapping = {
        "linux": OSType.LINUX,
        "windows": OSType.WINDOWS
    }

    try:
        os_option = os_option_mapping[os_option_str]
    except KeyError:
        pytest.fail("Please provide a valid OS option: --os=linux or --os=windows")

    if os_option == OSType.LINUX:
        host = get_env_var('LINUX_HOST')
        user = get_env_var('LINUX_USER')
        password = os.getenv('LINUX_PASSWORD')
        client = SSHClient(host, user, password)
    elif os_option == OSType.WINDOWS:
        host = get_env_var('WINDOWS_HOST')
        user = get_env_var('WINDOWS_USER')
        password = get_env_var('WINDOWS_PASSWORD')
        client = WinRMClient(host, user, password)
    else:
        pytest.fail("Unhandled OS type.")

    with client as c:
        yield c


@pytest.mark.parametrize("shell_client", [OSType.LINUX.value, OSType.WINDOWS.value], indirect=True)
@pytest.mark.linux
@pytest.mark.windows
def test_create_directory(shell_client: Union[SSHClient, WinRMClient], full_directory_path: str):
    assert full_directory_path, "No directory path specified"
    base_dir = get_base_dir()

    local_script, remote_script = get_script_paths(shell_client, base_dir, full_directory_path)
    assert os.path.exists(local_script), f"Script {local_script} does not exist."

    original_file_checksum = calculate_checksum(local_script)

    try:
        shell_client.upload_file(local_script, remote_script)

        remote_file_checksum = shell_client.get_file_checksum(remote_script, original_file_checksum)

        assert_equal_ignore_case(original_file_checksum, remote_file_checksum)

        shell_client.execute_script(remote_script, full_directory_path)

        assert shell_client.check_directory_exists(full_directory_path), f"Directory {full_directory_path} not created"

    finally:
        delete_remote_script(shell_client, remote_script)
