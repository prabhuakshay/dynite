"""Tests for the Client class in dynite.client module."""

from unittest.mock import patch

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


class TestClientBuildURL:
    """Tests for the _build_url method of the Client class."""

    def test_client_build_url_method(self) -> None:
        """Test the _build_url method of the Client class."""
        url = "https://example.com/odata/"
        auth = ("user", "pass")

        client_instance = Dynite(base_url=url, auth=auth)
        endpoint = "entities"
        params = {"filter": "name eq 'test'", "top": "10"}
        built_url = client_instance._build_url(endpoint, params)
        expected_url = (
            "https://example.com/odata/entities?filter=name+eq+%27test%27&top=10"
        )
        assert built_url == expected_url

    def test_client_build_url_no_params(self) -> None:
        """Test the _build_url method without query parameters."""
        url = "https://example.com/odata/"
        auth = ("user", "pass")
        client_instance = Dynite(base_url=url, auth=auth)
        endpoint = "entities"
        built_url = client_instance._build_url(endpoint)
        expected_url = "https://example.com/odata/entities"
        assert built_url == expected_url

    def test_client_build_url_leading_slash(self) -> None:
        """Test the _build_url method with an endpoint that has a leading slash."""
        url = "https://example.com/odata/"
        auth = ("user", "pass")
        client_instance = Dynite(base_url=url, auth=auth)
        endpoint = "/entities"
        built_url = client_instance._build_url(endpoint)
        expected_url = "https://example.com/odata/entities"
        assert built_url == expected_url

    def test_client_build_url_get_count(self) -> None:
        """Test the _build_url method with get_count flag set to True."""
        url = "https://example.com/odata/"
        auth = ("user", "pass")
        client_instance = Dynite(base_url=url, auth=auth)
        endpoint = "entities"
        built_url = client_instance._build_url(endpoint, get_count=True)
        expected_url = "https://example.com/odata/entities/$count"
        assert built_url == expected_url


class TestClientGetRecordCount:
    """Tests for the _get_record_count method of the Client class."""

    @patch("dynite.client.requests.Session.get")
    def test_client_get_record_count_method(self, mock_get: patch) -> None:
        """Test the _get_record_count method of the Client class."""
        url = "https://example.com/odata/"
        auth = ("user", "pass")
        client_instance = Dynite(base_url=url, auth=auth)

        # Mock the session.get response
        mock_response = mock_get.return_value
        mock_response.content = b"42"
        mock_response.raise_for_status.return_value = None

        endpoint = "entities"
        record_count = client_instance._get_record_count(endpoint)

        assert record_count == 42
        mock_get.assert_called_once_with(
            "https://example.com/odata/entities/$count", timeout=30
        )
