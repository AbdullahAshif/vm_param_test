# utils/assertions.py

def assert_strings_equal(expected: str, actual: str, message: str = None):
    if expected.lower() != actual.lower():
        error_message = message or f"Strings do not match. Expected: {expected}, Got: {actual}"
        raise ValueError(error_message)
