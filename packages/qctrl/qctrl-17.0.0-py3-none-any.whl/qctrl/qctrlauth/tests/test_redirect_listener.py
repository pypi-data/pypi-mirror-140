"""
Tests for qctrlauth.redirect_listener module.
"""

import socket
from unittest.mock import call

import pytest

from qctrl.qctrlauth.redirect_listener import (
    check_if_network_port_is_available,
    complete_login,
    get_free_network_port,
)


def test_check_if_network_port_is_available():
    port = get_free_network_port()
    assert check_if_network_port_is_available(port) is True, "Port should be available"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("", port))
        sock.listen(1)
        assert (
            check_if_network_port_is_available(port) is False
        ), "Port shouldn't be available"
        sock.close()


def test_get_free_network_port():
    with pytest.raises(RuntimeError, match="No free network port found"):
        get_free_network_port(0, 0)


def test_complete_login(mocker):
    mocked_open = mocker.patch("webbrowser.open")
    mocked_handle = mocker.patch("http.server.HTTPServer.handle_request")

    port = get_free_network_port()
    complete_login(port, "http://test", lambda: None)

    assert mocked_open.called is True
    mocked_open.assert_has_calls([call("http://test")])
    assert mocked_handle.called is True


def test_complete_login_port_used():
    port = get_free_network_port()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("", port))
        sock.listen(1)
        with pytest.raises(RuntimeError, match="port is already in use"):
            complete_login(port, "http://test", lambda: None)
        sock.close()
