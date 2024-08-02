# VM Test Project

## Overview
This project contains scripts to create a directory on a remote Windows or Linux VM, upload the script, verify the upload, execute it, and verify the directory creation using parameterized tests.

## Project Structure
- `src/`: Contains the base and specific shell clients for Linux and Windows.
- `tests/`: Contains parameterized tests using pytest.
- `requirements.txt`: List of required Python packages.

## Setup
1. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

## Running Tests
Execute the tests using pytest:
```sh
pytest tests/test_vm.py --dirpath "C:/your/full/path/to/create/test_directory"
