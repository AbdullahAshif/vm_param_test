# This is to check if the local host can connect with Windows based OS VM
import os
import pytest
from dotenv import load_dotenv
from src.winrm_client import WinRMClient

# Load environment variables from .env file
load_dotenv()


@pytest.fixture
def windows_rm_client():
    host = os.getenv('WINDOWS_HOST')
    username = os.getenv('WINDOWS_USER')
    password = os.getenv('WINDOWS_PASSWORD')
    if not host or not username or not password:
        pytest.fail("WINRM credentials are not set in environment variables")
    return WinRMClient(host, username, password)


def test_windows_rm_connection(windows_rm_client):
    # Example command to test connection
    command = "dir"  # Windows command to list directory contents
    output = windows_rm_client.execute_command(command)
    assert output, "Command output is empty"
    print(output)
