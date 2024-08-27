# utils/environment_utils.py
import os


def verify_env_vars_exist(*vars):
    missing_vars = [var for var in vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")
