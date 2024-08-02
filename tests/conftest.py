# tests/conftest.py
import pytest


def pytest_addoption(parser):
    parser.addoption("--dirpath", action="store", default=None, help="Full directory path to create")
    parser.addoption("--os", action="store", default=None,
                     help="Comma-separated list of OS types to test (e.g., linux,windows)")


@pytest.fixture
def os_list(request):
    os_types = request.config.getoption("--os")
    return os_types.split(",") if os_types else []
