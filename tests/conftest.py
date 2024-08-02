# tests/conftest.py
import pytest


def pytest_addoption(parser):
    parser.addoption("--dirpath", action="store", default=None, help="Full directory path to create")
