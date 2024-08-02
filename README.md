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
    ```sh
    pip install -r requirements.txt
    ```

2. Create `.env` file in root directory with credentials for VM like `Hostname`, `Username` and `Password` for both Linux and Windows
3. Make sure that the VM where you're trying to create directory with this codes have WinRM `Windows based OS` and SSH `Linux based OS` enabled 

## Running Tests
Execute the tests using pytest:
```sh
pytest tests/test_vm.py --dirpath "C:/your/full/path/to/create/test_directory"
