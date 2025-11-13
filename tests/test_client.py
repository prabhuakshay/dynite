"""Tests for the Client class in dynite.client module."""

import pytest

from dynite.client import Dynite
from dynite.exceptions import InvalidURLError


class TestClientInitialization:
    """Tests for Client class initialization."""

    def test_client_initialization(self) -> None:
        """Test that the Client class initializes correctly with a valid base URL."""
        url = "https://example.com/odata/"
        client_instance = Dynite(base_url=url)
        assert isinstance(client_instance, Dynite)
        assert client_instance.base_url == url.rstrip("/")

    def test_validate_url_invalid(self) -> None:
        """Test that the Client class raises InvalidURLError for invalid base URLs."""
        invalid_url = "ftp://example.com/odata/"
        with pytest.raises(InvalidURLError):
            _ = Dynite(base_url=invalid_url)

    def test_validate_url_trailing_slash(self) -> None:
        """Test that the Client class removes trailing slashes from the base URL."""
        url_with_slash = "https://example.com/odata/"
        url_without_slash = "https://example.com/odata"
        client_instance = Dynite(base_url=url_with_slash)
        assert client_instance.base_url == url_without_slash
        client_instance_no_slash = Dynite(base_url=url_without_slash)
        assert client_instance_no_slash.base_url == url_without_slash
