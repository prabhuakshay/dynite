"""Tests for the Client class in dynite.client module."""

import pytest
from requests.adapters import HTTPAdapter

from dynite import Dynite
from dynite.exceptions import InvalidURLError


class TestClientInitialization:
    """Tests for Client class initialization."""

    def test_client_initialization(self) -> None:
        """Test that the Client class initializes without errors."""
        auth: tuple[str, str] = ("user", "pass")
        url = "https://example.com/odata/"
        client_instance = Dynite(base_url=url, auth=auth)
        assert isinstance(client_instance, Dynite)

    def test_client_base_url_with_slash(self) -> None:
        """Test base_url attribute is set correctly when it ends with a slash."""
        auth: tuple[str, str] = ("user", "pass")
        url_with_slash = "https://example.com/odata/"
        client_instance_with_slash = Dynite(base_url=url_with_slash, auth=auth)
        assert client_instance_with_slash.base_url == "https://example.com/odata"

    def test_client_base_url_without_slash(self) -> None:
        """Test base_url attribute is set correctly when it does notend with a slash."""
        auth: tuple[str, str] = ("user", "pass")
        url_without_slash = "https://example.com/odata"
        client_instance_no_slash = Dynite(base_url=url_without_slash, auth=auth)
        assert client_instance_no_slash.base_url == "https://example.com/odata"

    def test_client_invalid_base_url(self) -> None:
        """Test that providing an invalid base_url raises an InvalidURLError."""
        auth: tuple[str, str] = ("user", "pass")
        not_a_url = "ftp://example.com/odata/"
        with pytest.raises(InvalidURLError):
            _ = Dynite(base_url=not_a_url, auth=auth)

    def test_client_invalid_base_url_no_netloc(self) -> None:
        """Test that providing a base_url with scheme but no netloc."""
        auth: tuple[str, str] = ("user", "pass")
        no_netloc_url = "https://"
        with pytest.raises(InvalidURLError):
            _ = Dynite(base_url=no_netloc_url, auth=auth)

    def test_client_timeout_default(self) -> None:
        """Test that the timeout attribute is set to the default value."""
        url = "https://example.com/odata/"
        auth: tuple[str, str] = ("user", "pass")
        client_instance = Dynite(base_url=url, auth=auth)
        assert client_instance._timeout == 30

    def test_client_timeout_custom(self) -> None:
        """Test that the timeout attribute is set to a custom value."""
        url = "https://example.com/odata/"
        auth: tuple[str, str] = ("user", "pass")
        custom_timeout = 10
        client_instance = Dynite(base_url=url, auth=auth, timeout=custom_timeout)
        assert client_instance._timeout == custom_timeout

    def test_client_timeout_invalid(self) -> None:
        """Test that providing an invalid timeout raises a ValueError."""
        url = "https://example.com/odata/"
        auth: tuple[str, str] = ("user", "pass")
        invalid_timeout = -5
        client_instance = Dynite(base_url=url, auth=auth, timeout=invalid_timeout)
        assert client_instance._timeout == 30  # Should default to 30 on invalid input

    def test_client_retries_default(self) -> None:
        """Test that the retries attribute is set to the default value."""
        url = "https://example.com/odata/"
        auth: tuple[str, str] = ("user", "pass")
        client_instance = Dynite(base_url=url, auth=auth)
        adapter = client_instance.session.get_adapter("http://")
        assert isinstance(adapter, HTTPAdapter)
        assert adapter.max_retries.total == 3

    def test_client_retries_custom(self) -> None:
        """Test that the retries attribute is set to a custom value."""
        url = "https://example.com/odata/"
        auth: tuple[str, str] = ("user", "pass")
        custom_retries = 5
        client_instance = Dynite(base_url=url, auth=auth, retries=custom_retries)
        adapter = client_instance.session.get_adapter("http://")
        assert isinstance(adapter, HTTPAdapter)
        assert adapter.max_retries.total == custom_retries

    def test_client_retries_invalid(self) -> None:
        """Test that providing an invalid retries value raises a ValueError."""
        url = "https://example.com/odata/"
        auth: tuple[str, str] = ("user", "pass")
        invalid_retries = -1
        client_instance = Dynite(base_url=url, auth=auth, retries=invalid_retries)
        adapter = client_instance.session.get_adapter("http://")
        assert isinstance(adapter, HTTPAdapter)
        assert adapter.max_retries.total == 3  # Should default to 3 on invalid input

    def test_client_session_adapters(self) -> None:
        """Test that the session has HTTP and HTTPS adapters set."""
        url = "https://example.com/odata/"
        auth: tuple[str, str] = ("user", "pass")
        client_instance = Dynite(base_url=url, auth=auth)
        assert isinstance(client_instance.session.get_adapter("http://"), HTTPAdapter)
        assert isinstance(client_instance.session.get_adapter("https://"), HTTPAdapter)
