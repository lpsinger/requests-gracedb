from pytest_socket import disable_socket


def pytest_runtest_setup():
    """Pytest setup hook."""
    disable_socket()
