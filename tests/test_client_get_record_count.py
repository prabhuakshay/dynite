"""Test Dynite client get_record_count functionality."""

import responses

from dynite import Dynite


class TestClientGetRecordCount:
    """Tests for the _get_record_count method of the Client class."""

    URL: str = "https://example.com/odata/"
    AUTH: tuple[str, str] = ("user", "pass")
    CLIENT: Dynite = Dynite(base_url=URL, auth=AUTH)

    @responses.activate
    def test_client_get_record_count_method(self) -> None:
        """Test the _get_record_count method of the Client class."""
        responses.add(
            responses.GET,
            self.CLIENT._build_url("entities", get_count=True),
            body="42",
            status=200,
            content_type="text/plain",
        )

        record_count = self.CLIENT._get_record_count("entities")
        assert record_count == 42

    @responses.activate
    def test_client_get_record_count_method_with_params(self) -> None:
        """Test the _get_record_count method with query parameters."""
        params = {"filter": "name eq 'test'"}
        expected_url = self.CLIENT._build_url("entities", params, get_count=True)

        responses.add(
            responses.GET,
            expected_url,
            body="15",
            status=200,
            content_type="text/plain",
        )

        record_count = self.CLIENT._get_record_count("entities", params)
        assert record_count == 15
