"""Test for the _get method of the Dynite client."""

import pytest
import responses

from dynite import Dynite
from dynite.exceptions import FailedRequestError


class TestClientGet:
    """Tests for the _get method of the Dynite client."""

    URL: str = "https://example.com/odata/"
    AUTH: tuple[str, str] = ("user", "pass")
    CLIENT: Dynite = Dynite(base_url=URL, auth=AUTH)
    ENDPOINT: str = "entities"

    @responses.activate
    def test_client_get_method(self) -> None:
        """Test the _get method of the Dynite client."""
        responses.add(
            responses.GET,
            self.CLIENT._build_url(self.ENDPOINT),
            json={"value": [{"id": 1}, {"id": 2}]},
            status=200,
        )

        response = self.CLIENT._get(self.CLIENT._build_url(self.ENDPOINT))
        assert response.status_code == 200
        assert response.json() == {"value": [{"id": 1}, {"id": 2}]}

    # Test for all non success codes raise FailedRequestError
    @responses.activate
    @pytest.mark.parametrize("status_code", [400, 401, 403, 404, 500])
    def test_client_get_method_failed_request(self, status_code: int) -> None:
        """Test the _get method handling of HTTP errors."""
        responses.add(
            responses.GET,
            self.CLIENT._build_url(self.ENDPOINT),
            body="Error",
            status=status_code,
        )
        with pytest.raises(FailedRequestError):
            self.CLIENT._get(self.CLIENT._build_url(self.ENDPOINT))
