"""Test Dynite client"""

import pytest
from requests.adapters import HTTPAdapter

from dynite import Dynite
from dynite.exceptions import InvalidURLError


# ============================================================
# Test Dynite Client Initialization
# ============================================================
class TestDyniteInitialization:
    """Test Dynite client initialization."""

    def test_client_initialization_success(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that the Dynite client initializes correctly."""
        client = Dynite(base_url=base_url, auth=auth)
        assert isinstance(client, Dynite)
        assert client.base_url == base_url
        assert client.session.auth == auth


# ============================================================
# Test Dynite Base URL Handling
# ============================================================
class TestDyniteBaseURLHandling:
    def test_client_initialization_invalid_url(self, auth: tuple[str, str]) -> None:
        """Test that the Dynite client raises an error for invalid URL."""
        invalid_url = "invalid_url"
        with pytest.raises(InvalidURLError):
            _ = Dynite(base_url=invalid_url, auth=auth)

    def test_client_initialization_url_with_slash(self, auth: tuple[str, str]) -> None:
        """Test that the Dynite client handles base_url with trailing slash."""
        url_with_slash = "https://example.com/odata/"
        client = Dynite(base_url=url_with_slash, auth=auth)
        assert client.base_url == "https://example.com/odata"

    def test_client_initialization_url_without_slash(
        self, auth: tuple[str, str]
    ) -> None:
        """Test that the Dynite client handles base_url without trailing slash."""
        url_without_slash = "https://example.com/odata"
        client = Dynite(base_url=url_without_slash, auth=auth)
        assert client.base_url == "https://example.com/odata"

    def test_client_initialization_url_no_netloc(self, auth: tuple[str, str]) -> None:
        """Test that the Dynite client raises an error for URL with no netloc."""
        no_netloc_url = "https://"
        with pytest.raises(InvalidURLError):
            _ = Dynite(base_url=no_netloc_url, auth=auth)


# ============================================================
# Test Dynite Timeout Handling
# ============================================================
class TestDyniteTimeoutHandling:
    def test_client_initialization_with_timeout(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that the Dynite client initializes with a custom timeout."""
        custom_timeout = 15
        client = Dynite(base_url=base_url, auth=auth, timeout=custom_timeout)
        assert client._timeout == custom_timeout

    def test_client_initialization_default_timeout(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that the Dynite client initializes with the default timeout."""
        client = Dynite(base_url=base_url, auth=auth)
        assert client._timeout == Dynite.DEFAULT_TIMEOUT

    def test_client_initialization_invalid_timeout(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that the Dynite client raises an error for invalid timeout."""
        invalid_timeout = -5
        client = Dynite(base_url=base_url, auth=auth, timeout=invalid_timeout)
        assert client._timeout == Dynite.DEFAULT_TIMEOUT


# ============================================================
# Test Dynite Auth and Retry Handling
# ============================================================
class TestDyniteAuthHandling:
    def test_client_initialization_with_auth(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that the Dynite client initializes with authentication."""
        client = Dynite(base_url=base_url, auth=auth)
        assert client.session.auth == auth


# ============================================================
# Test Dynite Retry Handling
# ============================================================
class TestDyniteRetryHandling:
    def test_client_initialization_with_retries(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that the Dynite client initializes with custom retries."""
        custom_retries = 5
        client = Dynite(base_url=base_url, auth=auth, retries=custom_retries)
        handler = client.session.get_adapter("https://")
        assert handler.max_retries.total == custom_retries

    def test_client_initialization_default_retries(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that the Dynite client initializes with default retries."""
        client = Dynite(base_url=base_url, auth=auth)
        handler = client.session.get_adapter("https://")
        assert handler.max_retries.total == Dynite.DEFAULT_RETRIES

    def test_client_initialization_invalid_retries(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that the Dynite client raises an error for invalid retries."""
        invalid_retries = -1
        client = Dynite(base_url=base_url, auth=auth, retries=invalid_retries)
        handler = client.session.get_adapter("https://")
        assert handler.max_retries.total == Dynite.DEFAULT_RETRIES


# ============================================================
# Test Dynite Session Adapters
# ============================================================
class TestDyniteSessionAdapters:
    def test_client_session_adapters_set(
        self, base_url: str, auth: tuple[str, str]
    ) -> None:
        """Test that the Dynite client session has HTTP and HTTPS adapters set."""
        client = Dynite(base_url=base_url, auth=auth)
        http_adapter = client.session.get_adapter("http://")
        https_adapter = client.session.get_adapter("https://")
        assert isinstance(http_adapter, HTTPAdapter)
        assert isinstance(https_adapter, HTTPAdapter)
