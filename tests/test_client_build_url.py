"""Tests for building URLs in the Dynite client."""

from dynite import Dynite


class TestClientBuildURL:
    """Test client build URL functionality."""

    URL = "https://example.com/odata/"
    AUTH: tuple[str, str] = ("user", "pass")
    ENDPOINT: str = "entities"
    CLIENT: Dynite = Dynite(base_url=URL, auth=AUTH)

    def test_with_parameters(self) -> None:
        """Test building URL with parameters."""
        params = {"filter": "name eq 'test'", "top": "10"}
        built_url = self.CLIENT._build_url(self.ENDPOINT, params)
        expected_url = (
            "https://example.com/odata/entities?filter=name+eq+%27test%27&top=10"
        )
        assert built_url == expected_url

    def test_without_parameters(self) -> None:
        """Test building URL without parameters."""
        built_url = self.CLIENT._build_url(self.ENDPOINT)
        expected_url = "https://example.com/odata/entities"
        assert built_url == expected_url

    def test_leading_slash_endpoint(self) -> None:
        """Test building URL with leading slash in endpoint."""
        built_url = self.CLIENT._build_url(self.ENDPOINT)
        expected_url = "https://example.com/odata/entities"
        assert built_url == expected_url

    def test_get_count_url(self) -> None:
        """Test building URL with get_count flag."""
        built_url = self.CLIENT._build_url(self.ENDPOINT, get_count=True)
        built_url = self.CLIENT._build_url(self.ENDPOINT, get_count=True)
        expected_url = "https://example.com/odata/entities/$count"
        assert built_url == expected_url

    def test_get_count_url_with_params(self) -> None:
        """Test building URL with get_count flag and parameters."""
        built_url = self.CLIENT._build_url(
            self.ENDPOINT, {"filter": "name eq 'test'"}, get_count=True
        )
        params = {"filter": "name eq 'test'"}
        built_url = self.CLIENT._build_url(self.ENDPOINT, params, get_count=True)
        expected_url = (
            "https://example.com/odata/entities/$count?filter=name+eq+%27test%27"
        )
        assert built_url == expected_url
