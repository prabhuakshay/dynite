"""Test suite for Dynite client initialization and configuration.

This module contains comprehensive tests for the Dynite client initialization
process, including URL validation, timeout configuration, authentication setup,
retry logic, and session adapter configuration. These tests ensure that the
client is properly configured for various scenarios and handles invalid inputs
gracefully.

Test categories:
- Basic client initialization with valid parameters
- URL validation and normalization
- Timeout parameter handling
- Authentication configuration
- Retry strategy setup
- HTTP adapter configuration
"""

import pytest
from requests.adapters import HTTPAdapter

from dynite import Dynite
from dynite.exceptions import InvalidURLError


# ============================================================
# Test Dynite Client Initialization
# ============================================================
class TestDyniteInitialization:
    """Test cases for basic Dynite client initialization."""

    def test_client_initialization_success(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test successful initialization of Dynite client with valid parameters.

        Verifies that a Dynite client can be created with proper base URL and
        authentication credentials, and that the resulting object has the
        expected attributes set correctly.

        Args:
            base_url (str): Mock base URL fixture.
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        client = Dynite(base_url=base_url, auth=auth)
        assert isinstance(client, Dynite)
        assert client.base_url == base_url
        assert client.session.auth == auth


# ============================================================
# Test Dynite Base URL Handling
# ============================================================
class TestDyniteBaseURLHandling:
    """Test cases for URL validation and normalization during initialization."""

    def test_client_initialization_invalid_url(self, auth: tuple[str, str]) -> None:
        """Test that invalid URLs raise InvalidURLError during initialization.

        Ensures that the client properly validates the base URL format and
        raises an appropriate exception for malformed URLs that don't meet
        the required HTTP/HTTPS scheme and netloc requirements.

        Args:
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        invalid_url = "invalid_url"
        with pytest.raises(InvalidURLError):
            _ = Dynite(base_url=invalid_url, auth=auth)

    def test_client_initialization_url_with_slash(self, auth: tuple[str, str]) -> None:
        """Test that trailing slashes are properly stripped from base URLs.

        Verifies that the client normalizes URLs by removing trailing slashes,
        ensuring consistent URL construction for API endpoints regardless of
        how the base URL is provided.

        Args:
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        url_with_slash = "https://example.com/odata/"
        client = Dynite(base_url=url_with_slash, auth=auth)
        assert client.base_url == "https://example.com/odata"

    def test_client_initialization_url_without_slash(
        self, auth: tuple[str, str]
    ) -> None:
        """Test that URLs without trailing slashes are handled correctly.

        Confirms that the client accepts and stores URLs without trailing
        slashes without modification, maintaining the expected base URL format.

        Args:
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        url_without_slash = "https://example.com/odata"
        client = Dynite(base_url=url_without_slash, auth=auth)
        assert client.base_url == "https://example.com/odata"

    def test_client_initialization_url_no_netloc(self, auth: tuple[str, str]) -> None:
        """Test that URLs without a valid network location raise InvalidURLError.

        Ensures that URLs like 'https://' (missing domain) are rejected during
        initialization, preventing connection attempts to invalid endpoints.

        Args:
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        no_netloc_url = "https://"
        with pytest.raises(InvalidURLError):
            _ = Dynite(base_url=no_netloc_url, auth=auth)


# ============================================================
# Test Dynite Timeout Handling
# ============================================================
class TestDyniteTimeoutHandling:
    """Test cases for timeout parameter validation and default handling."""

    def test_client_initialization_with_timeout(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that custom timeout values are properly set during initialization.

        Verifies that when a valid timeout is provided, it is stored in the
        client's _timeout attribute for use in subsequent API requests.

        Args:
            base_url (str): Mock base URL fixture.
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        custom_timeout = 15
        client = Dynite(base_url=base_url, auth=auth, timeout=custom_timeout)
        assert client._timeout == custom_timeout

    def test_client_initialization_default_timeout(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that the default timeout is used when none is specified.

        Ensures that when no timeout parameter is provided, the client uses
        the DEFAULT_TIMEOUT class constant, maintaining predictable behavior.

        Args:
            base_url (str): Mock base URL fixture.
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        client = Dynite(base_url=base_url, auth=auth)
        assert client._timeout == Dynite.DEFAULT_TIMEOUT

    def test_client_initialization_invalid_timeout(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that invalid timeout values fall back to the default.

        Verifies that negative or zero timeout values are rejected and the
        client automatically uses the DEFAULT_TIMEOUT instead, preventing
        indefinite hangs on network requests.

        Args:
            base_url (str): Mock base URL fixture.
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        invalid_timeout = -5
        client = Dynite(base_url=base_url, auth=auth, timeout=invalid_timeout)
        assert client._timeout == Dynite.DEFAULT_TIMEOUT


# ============================================================
# Test Dynite Auth and Retry Handling
# ============================================================
class TestDyniteAuthHandling:
    """Test cases for authentication configuration."""

    def test_client_initialization_with_auth(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that authentication credentials are properly configured.

        Ensures that the provided authentication tuple is correctly assigned
        to the requests session, enabling authenticated API requests.

        Args:
            base_url (str): Mock base URL fixture.
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        client = Dynite(base_url=base_url, auth=auth)
        assert client.session.auth == auth


# ============================================================
# Test Dynite Retry Handling
# ============================================================
class TestDyniteRetryHandling:
    """Test cases for retry strategy configuration."""

    def test_client_initialization_with_retries(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that custom retry counts are properly configured.

        Verifies that when a custom retry value is provided, it is correctly
        applied to the HTTP adapters for both HTTP and HTTPS requests.

        Args:
            base_url (str): Mock base URL fixture.
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        custom_retries = 5
        client = Dynite(base_url=base_url, auth=auth, retries=custom_retries)
        handler = client.session.get_adapter("https://")
        assert handler.max_retries.total == custom_retries

    def test_client_initialization_default_retries(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that default retry settings are applied when none specified.

        Ensures that when no retry parameter is provided, the client uses
        the DEFAULT_RETRIES value, providing consistent retry behavior.

        Args:
            base_url (str): Mock base URL fixture.
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        client = Dynite(base_url=base_url, auth=auth)
        handler = client.session.get_adapter("https://")
        assert handler.max_retries.total == Dynite.DEFAULT_RETRIES

    def test_client_initialization_invalid_retries(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that invalid retry values fall back to the default.

        Verifies that negative retry values are rejected and the client
        automatically uses DEFAULT_RETRIES, preventing infinite retry loops.

        Args:
            base_url (str): Mock base URL fixture.
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        invalid_retries = -1
        client = Dynite(base_url=base_url, auth=auth, retries=invalid_retries)
        handler = client.session.get_adapter("https://")
        assert handler.max_retries.total == Dynite.DEFAULT_RETRIES


# ============================================================
# Test Dynite Session Adapters
# ============================================================
class TestDyniteSessionAdapters:
    """Test cases for HTTP adapter configuration."""

    def test_client_session_adapters_set(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that HTTP and HTTPS adapters are properly configured.

        Ensures that the client's session has HTTPAdapter instances mounted
        for both HTTP and HTTPS protocols, enabling retry logic and proper
        request handling for API calls.

        Args:
            base_url (str): Mock base URL fixture.
            auth (tuple[str, str]): Mock authentication tuple fixture.
        """
        client = Dynite(base_url=base_url, auth=auth)
        http_adapter = client.session.get_adapter("http://")
        https_adapter = client.session.get_adapter("https://")
        assert isinstance(http_adapter, HTTPAdapter)
        assert isinstance(https_adapter, HTTPAdapter)
