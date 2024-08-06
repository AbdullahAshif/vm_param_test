# VM Test Project

## Overview
This project contains scripts to create a directory on a remote Windows or Linux VM, upload the script, verify the upload, execute it, and verify the directory creation using parameterized tests.

## Project Structure
- `scripts/`: Contains the scrpits which will be copied to Linux or Windows based VM and execute to create desired directory
- `src/`: Contains the base and specific shell clients for Linux and Windows.
- `tests/`: Contains parameterized tests using pytest.
- `requirements.txt`: List of required Python packages.

## Setup
1. Install the required packages:
    ```shell
    pip install -r requirements.txt
    ```

2. Create `.env` file in root directory with credentials for VM like `Hostname`, `Username` and `Password` for both Linux and Windows
3. Make sure that the VM where you're trying to create directory with these codes have WinRM for `Windows based OS` and SSH for `Linux based OS` is enabled 

## Running Tests
Execute the tests using pytest:
- Running on both Windows and Linux VM sametime:
```shell
pytest tests/test_vm.py --dirpath "C:/your/full/path/to/create/test_directory" --os windows,linux
```
- Running on either Windows or Linux:
- For `Windows`:
```shell
pytest tests/test_vm.py --dirpath "C:/your/full/path/to/create/test_directory" --os windows
```
- For `Linux`:
```shell
pytest tests/test_vm.py --dirpath "your/full/path/to/create/test_directory" --os linux
```
