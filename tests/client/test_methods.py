"""Test client methods."""

from urllib.parse import urlencode

import pytest
import requests
import responses

from dynite import Dynite
from dynite.exceptions import FailedRequestError, InvalidResponseError


# ============================================================
# Helper Function to Build Expected URL
# ============================================================
def build_expected_url(
    base_url: str,
    endpoint: str,
    params: dict[str, str],
    *,
    get_count: bool = False,
) -> str:
    """Helper function to build expected URL."""
    if endpoint.startswith("/"):
        endpoint = endpoint.lstrip("/")
    url = f"{base_url}/{endpoint}"
    if get_count:
        url = f"{url}/$count"
    if params:
        query_string = urlencode(params)
        url = f"{url}?{query_string}"
    return url


# ============================================================
# Test Dynite Client build_url Method
# ============================================================
class TestClientBuildURL:
    # Without parameters
    def test_build_url_without_parameters(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that build_url appends endpoint correctly to base_url."""
        built_url = client._build_url(endpoint)
        expected_url = build_expected_url(base_url, endpoint, {})
        assert built_url == expected_url

    # With parameters
    def test_build_url_with_parameters(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that build_url appends query parameters correctly."""
        params = {"param1": "value1", "param2": "value2"}
        built_url = client._build_url(endpoint, params=params)
        expected_url = build_expected_url(base_url, endpoint, params)
        assert built_url == expected_url

    # Without parameters, with leading slash
    def test_build_url_with_leading_slash(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that build_url handles endpoint with leading slash."""
        endpoint = "/" + endpoint
        built_url = client._build_url(endpoint)
        expected_url = build_expected_url(base_url, endpoint, {})
        assert built_url == expected_url

    # With parameters, with leading slash
    def test_build_url_with_leading_slash_and_parameters(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that build_url handles leading slash and query parameters."""
        endpoint = "/" + endpoint
        params = {"param1": "value1", "param2": "value2"}
        built_url = client._build_url(endpoint, params=params)
        expected_url = build_expected_url(base_url, endpoint, params)
        assert built_url == expected_url

    # With get_count True
    def test_build_url_with_get_count(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that build_url appends $count correctly when get_count is True."""
        built_url = client._build_url(endpoint, get_count=True)
        expected_url = build_expected_url(base_url, endpoint, {}, get_count=True)
        assert built_url == expected_url

    # With parameters and get_count True
    def test_build_url_with_parameters_and_get_count(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that build_url appends query parameters and $count correctly."""
        params = {"param1": "value1", "param2": "value2"}
        built_url = client._build_url(endpoint, params=params, get_count=True)
        expected_url = build_expected_url(base_url, endpoint, params, get_count=True)
        assert built_url == expected_url


# ============================================================
# Test Dynite Client _get Method
# ============================================================
class TestClientGetMethod:
    @responses.activate
    def test_get_method_success_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that _get method successfully retrieves data from the API."""
        url = build_expected_url(base_url, endpoint, {})
        _ = responses.add(responses.GET, url, json={"key": "value"}, status=200)
        response = client._get(url)
        assert response.status_code == 200
        assert response.json() == {"key": "value"}

    @responses.activate
    @pytest.mark.parametrize("status_code", [400, 401, 403, 404, 500])
    def test_get_method_failure_handling(
        self, client: Dynite, endpoint: str, base_url: str, status_code: int
    ) -> None:
        """Test that _get method raises FailedRequestError on request failure."""
        url = build_expected_url(base_url, endpoint, {})
        _ = responses.add(
            responses.GET, url, json={"error": "not found"}, status=status_code
        )
        with pytest.raises(FailedRequestError):
            _ = client._get(url)

    @responses.activate
    def test_get_method_timeout_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that _get method raises FailedRequestError on timeout."""
        url = build_expected_url(base_url, endpoint, {})
        _ = responses.add(
            responses.GET,
            url,
            body=requests.exceptions.Timeout(),
        )
        with pytest.raises(FailedRequestError):
            _ = client._get(url)


# ============================================================
# Test Dynite Client _get_record_count Method
# ============================================================
class TestClientGetRecordCountMethod:
    @responses.activate
    def test_get_record_count_success_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that _get_record_count method retrieves the correct count."""
        url = build_expected_url(base_url, endpoint, {}, get_count=True)
        _ = responses.add(responses.GET, url, body="42", status=200)
        count = client._get_record_count(endpoint)
        assert count == 42

    @responses.activate
    def test_get_record_count_failure_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that _get_record_count method raise FailedRequestError on failure."""
        url = build_expected_url(base_url, endpoint, {}, get_count=True)
        _ = responses.add(responses.GET, url, json={"error": "not found"}, status=404)
        with pytest.raises(FailedRequestError):
            _ = client._get_record_count(endpoint)

    @responses.activate
    def test_get_record_count_invalid_response_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that _get_record_count method raises error on invalid response."""
        url = build_expected_url(base_url, endpoint, {}, get_count=True)
        _ = responses.add(responses.GET, url, body="not_a_number", status=200)
        with pytest.raises(InvalidResponseError):
            _ = client._get_record_count(endpoint)

    @responses.activate
    def test_get_record_count_with_parameters(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that _get_record_count method works with query parameters."""
        params = {"filter": "status eq 'active'"}
        url = build_expected_url(base_url, endpoint, params, get_count=True)
        _ = responses.add(responses.GET, url, body="15", status=200)
        count = client._get_record_count(endpoint, params=params)
        assert count == 15


# ============================================================
# Test Dynite client _get_next_page_link Method
# ============================================================
class TestClientGetNextPageLinkMethod:
    def test_get_next_page_link_present(self, client: Dynite, next_link: str) -> None:
        """Test that _get_next_page_link extracts the next page link when present."""
        response = {"@odata.nextLink": next_link}
        extracted_link = client._get_next_page_link(response)
        assert extracted_link == next_link

    def test_get_next_page_link_absent(self, client: Dynite) -> None:
        """Test that _get_next_page_link returns None when no link is present."""
        response = {}
        extracted_link = client._get_next_page_link(response)
        assert extracted_link is None


# ============================================================
# Test Dynite Client get_records Method
# ============================================================
class TestClientGetRecordsMethod:
    @responses.activate
    def test_get_records_success_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that get_records method retrieves records successfully."""
        expected_url = build_expected_url(base_url, endpoint, {})
        records = [{"id": 1}, {"id": 2}, {"id": 3}]
        _ = responses.add(
            responses.GET,
            expected_url,
            json={"value": records},
            status=200,
        )
        _ = responses.add(
            responses.GET,
            expected_url + "/$count",
            body="200",
            status=200,
        )
        retrieved_records = client.get_records(endpoint)
        assert retrieved_records == records
        assert len(responses.calls) == 2

    @responses.activate
    def test_get_records_pagination_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that get_records method handles pagination correctly."""
        first_page_url = build_expected_url(base_url, endpoint, {})
        second_page_url = first_page_url + "?$skip=3"
        records_page_1 = [{"id": 1}, {"id": 2}, {"id": 3}]
        records_page_2 = [{"id": 4}, {"id": 5}]
        _ = responses.add(
            responses.GET,
            first_page_url,
            json={
                "value": records_page_1,
                "@odata.nextLink": second_page_url,
            },
            status=200,
        )
        _ = responses.add(
            responses.GET,
            second_page_url,
            json={"value": records_page_2},
            status=200,
        )
        _ = responses.add(
            responses.GET,
            first_page_url + "/$count",
            body="5",
            status=200,
        )
        retrieved_records = client.get_records(endpoint)
        assert retrieved_records == records_page_1 + records_page_2
        assert len(responses.calls) == 3

    @responses.activate
    def test_get_records_failure_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that get_records method raises FailedRequestError on failure."""
        expected_url = build_expected_url(base_url, endpoint, {})
        _ = responses.add(
            responses.GET,
            expected_url,
            json={"error": "not found"},
            status=404,
        )
        _ = responses.add(
            responses.GET,
            expected_url + "/$count",
            body="100",
            status=200,
        )
        with pytest.raises(FailedRequestError):
            _ = client.get_records(endpoint)

    @responses.activate
    def test_get_records_invalid_json_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that get_records method raises InvalidResponseError on invalid JSON."""
        expected_url = build_expected_url(base_url, endpoint, {})
        _ = responses.add(
            responses.GET,
            expected_url,
            body="Invalid JSON",
            status=200,
        )
        _ = responses.add(
            responses.GET,
            expected_url + "/$count",
            body="50",
            status=200,
        )
        with pytest.raises(InvalidResponseError):
            _ = client.get_records(endpoint)
