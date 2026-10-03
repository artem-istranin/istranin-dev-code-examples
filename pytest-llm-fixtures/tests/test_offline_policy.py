"""Keep the promised offline test boundary observable."""

import os
import socket

import pytest
from pytest_socket import SocketBlockedError


def test_default_suite_blocks_sockets_and_removes_provider_secrets():
    for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"):
        assert name not in os.environ
    with (
        pytest.warns(UserWarning, match="socket.socket"),
        pytest.raises(SocketBlockedError),
    ):
        socket.socket()
