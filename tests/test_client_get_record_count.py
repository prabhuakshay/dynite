"""Test Dynite client get_record_count functionality."""

import pytest
import responses

from dynite import Dynite
from dynite.exceptions import InvalidResponseError


class TestClientGetRecordCount:
    """Tests for the _get_record_count method of the Client class."""

    URL: str = "https://example.com/odata/"
    AUTH: tuple[str, str] = ("user", "pass")
    CLIENT: Dynite = Dynite(base_url=URL, auth=AUTH)
    ENDPOINT: str = "entities"

    @responses.activate
    def test_client_get_record_count_method(self) -> None:
        """Test the _get_record_count method of the Client class."""
        responses.add(
            responses.GET,
            self.CLIENT._build_url(self.ENDPOINT, get_count=True),
            body="42",
            status=200,
            content_type="text/plain",
        )

        record_count = self.CLIENT._get_record_count(self.ENDPOINT)
        assert record_count == 42

    @responses.activate
    def test_client_get_record_count_method_with_params(self) -> None:
        """Test the _get_record_count method with query parameters."""
        params = {"filter": "name eq 'test'"}
        expected_url = self.CLIENT._build_url(self.ENDPOINT, params, get_count=True)

        responses.add(
            responses.GET,
            expected_url,
            body="15",
            status=200,
            content_type="text/plain",
        )

        record_count = self.CLIENT._get_record_count(self.ENDPOINT, params)
        assert record_count == 15

    @responses.activate
    def test_client_get_record_count_invalid_response(self) -> None:
        """Test the _get_record_count method handling of HTTP errors."""
        responses.add(
            responses.GET,
            self.CLIENT._build_url(self.ENDPOINT, get_count=True),
            body="Not a number",
            status=200,
        )
        with pytest.raises(InvalidResponseError):
            self.CLIENT._get_record_count(self.ENDPOINT)
