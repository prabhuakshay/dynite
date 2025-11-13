"""Tests for the Client class in dynite.client module."""

import pytest
from requests.adapters import HTTPAdapter

from dynite.client import Dynite
from dynite.exceptions import InvalidURLError


class TestClientInitialization:
    """Tests for Client class initialization."""

    def test_client_initialization(self) -> None:
        """Test that the Client class initializes correctly with a valid base URL."""
        # Check that the client instance is created without errors
        url = "https://example.com/odata/"
        client_instance = Dynite(base_url=url, auth=("user", "pass"))
        assert isinstance(client_instance, Dynite)

    def test_client_attributes(self) -> None:
        """
        Test that the Client class has the expected attributes after initialization.

        Expected attributes:
            - base_url
            - session
        """
        url = "https://example.com/odata/"
        auth = ("user", "pass")
        client_instance = Dynite(base_url=url, auth=auth)
        # Check Dynite.base_url exists
        assert hasattr(client_instance, "base_url")
        # Check Dynite.session exists
        assert hasattr(client_instance, "session")
        # Check that session.auth is set correctly
        assert client_instance.session.auth == auth
        # Check that timeout attribute exists
        assert hasattr(client_instance, "_timeout")
        # Check that the adapters are mounted
        assert isinstance(client_instance.session.get_adapter("http://"), HTTPAdapter)
        assert isinstance(client_instance.session.get_adapter("https://"), HTTPAdapter)

    def test_client_url_attribute(self) -> None:
        """Test that the base_url attribute is set correctly."""
        auth = ("user", "pass")

        url_with_slash = "https://example.com/odata/"
        client_instance_with_slash = Dynite(base_url=url_with_slash, auth=auth)
        assert client_instance_with_slash.base_url == "https://example.com/odata"

        url_without_slash = "https://example.com/odata"
        client_instance_no_slash = Dynite(base_url=url_without_slash, auth=auth)
        assert client_instance_no_slash.base_url == "https://example.com/odata"

        invalid_url = "ftp://example.com/odata/"
        with pytest.raises(InvalidURLError):
            _ = Dynite(base_url=invalid_url, auth=auth)

    def test_client_timeout_attribute(self) -> None:
        """Test that the timeout attribute is set correctly."""
        url = "https://example.com/odata/"
        auth = ("user", "pass")

        # Test default timeout
        client_instance_default = Dynite(base_url=url, auth=auth)
        assert client_instance_default._timeout == 30

        # Test custom timeout
        custom_timeout = 60
        client_instance_custom = Dynite(base_url=url, auth=auth, timeout=custom_timeout)
        assert client_instance_custom._timeout == custom_timeout

        # Test invalid timeout (negative value)
        invalid_timeout = -10
        client_instance_invalid = Dynite(
            base_url=url, auth=auth, timeout=invalid_timeout
        )
        assert client_instance_invalid._timeout == 30

    def test_client_retries_attribute(self) -> None:
        """Test that the retries attribute is set correctly."""
        url = "https://example.com/odata/"
        auth = ("user", "pass")

        # Test default retries
        client_instance_default = Dynite(base_url=url, auth=auth)
        adapter = client_instance_default.session.get_adapter("http://")
        assert isinstance(adapter, HTTPAdapter)
        assert adapter.max_retries.total == 3

        # Test custom retries
        custom_retries = 5
        client_instance_custom = Dynite(base_url=url, auth=auth, retries=custom_retries)
        adapter = client_instance_custom.session.get_adapter("http://")
        assert isinstance(adapter, HTTPAdapter)
        assert adapter.max_retries.total == custom_retries

        # Test invalid retries (negative value)
        invalid_retries = -2
        client_instance_invalid = Dynite(
            base_url=url, auth=auth, retries=invalid_retries
        )
        adapter = client_instance_invalid.session.get_adapter("http://")
        assert isinstance(adapter, HTTPAdapter)
        assert adapter.max_retries.total == 3
