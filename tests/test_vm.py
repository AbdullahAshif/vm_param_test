import pytest
import os
from dotenv import load_dotenv
from src.ssh_client import SSHClient
from src.winrm_client import WinRMClient
from src.utils import get_base_dir, get_env_var
from src.shell_utils import get_script_paths
from src.constants import OSType
from typing import Union
from utils.environment_utils import verify_env_vars_exist
from utils.file_utils import compare_checksums

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
        verify_env_vars_exist('LINUX_HOST', 'LINUX_USER', 'LINUX_PASSWORD')
        host = get_env_var('LINUX_HOST')
        user = get_env_var('LINUX_USER')
        password = os.getenv('LINUX_PASSWORD')
        client = SSHClient(host, user, password)
    elif os_option == OSType.WINDOWS:
        verify_env_vars_exist('WINDOWS_HOST', 'WINDOWS_USER', 'WINDOWS_PASSWORD')
        host = get_env_var('WINDOWS_HOST')
        user = get_env_var('WINDOWS_USER')
        password = get_env_var('WINDOWS_PASSWORD')
        client = WinRMClient(host, user, password)
    else:
        pytest.fail("Unhandled OS type.")

    with client as c:
        yield c


@pytest.mark.linux
@pytest.mark.windows
def test_create_directory(shell_client: Union[SSHClient, WinRMClient], full_directory_path: str):
    base_dir = get_base_dir()

    local_script, remote_script = get_script_paths(shell_client, base_dir, full_directory_path)

    try:
        shell_client.upload_file(local_script, remote_script)
        compare_checksums(shell_client, local_script, remote_script)
        shell_client.execute_script(remote_script, full_directory_path)
        assert shell_client.is_directory_exists(full_directory_path), f"Directory {full_directory_path} not created"

    finally:
        shell_client.delete_file(remote_script)
