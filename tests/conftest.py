import pytest

from src.os_enum import OSType


def pytest_addoption(parser):
    parser.addoption("--os", action="store", default=None, help="Specify the OS: 'linux' or 'windows'")
    parser.addoption("--dirpath", action="store", default=None, help="Full directory path to create")
    parser.addoption("--dirname", action="store", default=None, help="Directory name to create")


def pytest_collection_modifyitems(config, items):
    os_option = config.getoption("--os")
    if os_option:
        keep = []
        for item in items:
            if any(mark.name == os_option for mark in item.own_markers):
                keep.append(item)
            else:
                item.add_marker(pytest.mark.skip(reason="Skipping this test because it's not for the specified OS"))
        items[:] = keep


@pytest.fixture
def full_directory_path(request):
    dirpath = request.config.getoption("--dirpath")
    dirname = request.config.getoption("--dirname")
    os_option = request.config.getoption("--os")
    if not dirpath or not dirname:
        pytest.fail("Please provide a directory path using --dirpath and --dirname options.")
    if os_option == OSType.LINUX.value:
        return f"{dirpath}/{dirname}"
    elif os_option == OSType.WINDOWS.value:
        return f"{dirpath}\\{dirname}"
    else:
        pytest.fail("Please provide a valid OS option: --os=linux or --os=windows")
