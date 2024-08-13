import hashlib
import os


def calculate_checksum(file_path, chunk_size=8192):
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as file:
        while chunk := file.read(chunk_size):
            sha256.update(chunk)
    return sha256.hexdigest()


def get_base_dir():
    return os.path.dirname(os.path.abspath(__file__))


def get_env_var(var_name):
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"Environment variable '{var_name}' is not set.")
    return value
