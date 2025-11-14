"""Test suite for Dynite client methods and API interactions.

This module contains comprehensive tests for all public and private methods
of the Dynite client, including URL building, HTTP requests, record counting,
pagination handling, and data retrieval. Tests use mocked responses to simulate
API interactions without making actual network calls.

Test categories:
- URL construction and parameter handling
- HTTP request execution and error handling
- Record count retrieval from OData $count endpoints
- Pagination link extraction
- Full record retrieval with automatic pagination
"""

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
    """Helper function to build expected URL for test assertions.

    Constructs URLs in the same way as the Dynite client's _build_url method,
    allowing tests to verify that URLs are built correctly. Handles endpoint
    normalization, query parameter encoding, and $count suffix appending.

    Args:
        base_url (str): The base URL of the API.
        endpoint (str): The API endpoint to append.
        params (dict[str, str]): Query parameters to include.
        get_count (bool, optional): Whether to append /$count for record counting.

    Returns:
        str: The fully constructed URL matching Dynite's URL building logic.
    """
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
    """Test cases for the _build_url private method."""

    # Without parameters
    def test_build_url_without_parameters(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test URL building without query parameters.

        Verifies that _build_url correctly combines base URL and endpoint
        when no additional parameters are provided, ensuring basic URL
        construction works as expected.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
        built_url = client._build_url(endpoint)
        expected_url = build_expected_url(base_url, endpoint, {})
        assert built_url == expected_url

    # With parameters
    def test_build_url_with_parameters(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test URL building with query parameters.

        Ensures that _build_url properly encodes and appends query parameters
        to the URL, maintaining correct parameter order and URL encoding.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
        params = {"param1": "value1", "param2": "value2"}
        built_url = client._build_url(endpoint, params=params)
        expected_url = build_expected_url(base_url, endpoint, params)
        assert built_url == expected_url

    # Without parameters, with leading slash
    def test_build_url_with_leading_slash(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test URL building handles endpoints with leading slashes.

        Verifies that _build_url strips leading slashes from endpoints,
        preventing double slashes in the final URL and ensuring consistent
        URL formatting regardless of endpoint format.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
        endpoint = "/" + endpoint
        built_url = client._build_url(endpoint)
        expected_url = build_expected_url(base_url, endpoint, {})
        assert built_url == expected_url

    # With parameters, with leading slash
    def test_build_url_with_leading_slash_and_parameters(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test URL building with both leading slash and parameters.

        Confirms that _build_url handles endpoints with leading slashes
        while still correctly appending query parameters, ensuring robust
        URL construction in all scenarios.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
        endpoint = "/" + endpoint
        params = {"param1": "value1", "param2": "value2"}
        built_url = client._build_url(endpoint, params=params)
        expected_url = build_expected_url(base_url, endpoint, params)
        assert built_url == expected_url

    # With get_count True
    def test_build_url_with_get_count(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test URL building with $count suffix for record counting.

        Ensures that when get_count=True, _build_url appends the /$count
        suffix to the endpoint, enabling OData record count queries.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
        built_url = client._build_url(endpoint, get_count=True)
        expected_url = build_expected_url(base_url, endpoint, {}, get_count=True)
        assert built_url == expected_url

    # With parameters and get_count True
    def test_build_url_with_parameters_and_get_count(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test URL building with both parameters and $count suffix.

        Verifies that _build_url correctly combines query parameters with
        the $count suffix, allowing filtered record counts to be retrieved.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
        params = {"param1": "value1", "param2": "value2"}
        built_url = client._build_url(endpoint, params=params, get_count=True)
        expected_url = build_expected_url(base_url, endpoint, params, get_count=True)
        assert built_url == expected_url


# ============================================================
# Test Dynite Client _get Method
# ============================================================
class TestClientGetMethod:
    """Test cases for the _get private method."""

    @responses.activate
    def test_get_method_success_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test successful HTTP GET request execution.

        Verifies that _get method successfully retrieves data from a mocked
        API endpoint, returning a proper Response object with correct status
        and JSON content.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
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
        """Test that _get raises FailedRequestError for HTTP error status codes.

        Ensures that non-2xx status codes from the API are properly caught
        and converted to FailedRequestError exceptions, providing consistent
        error handling for various failure scenarios.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
            status_code (int): HTTP status code to test (parametrized).
        """
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
        """Test that _get handles request timeouts properly.

        Verifies that when a request times out, a FailedRequestError is raised,
        ensuring that timeout conditions are handled consistently with other
        request failures.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
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
    """Test cases for the _get_record_count private method."""

    @responses.activate
    def test_get_record_count_success_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test successful retrieval of record count from $count endpoint.

        Ensures that _get_record_count correctly parses numeric responses
        from OData $count endpoints and returns the count as an integer.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
        url = build_expected_url(base_url, endpoint, {}, get_count=True)
        _ = responses.add(responses.GET, url, body="42", status=200)
        count = client._get_record_count(endpoint)
        assert count == 42

    @responses.activate
    def test_get_record_count_failure_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that _get_record_count raises FailedRequestError on HTTP failures.

        Verifies that when the $count endpoint returns an error status,
        the method properly raises FailedRequestError instead of returning
        invalid count data.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
        url = build_expected_url(base_url, endpoint, {}, get_count=True)
        _ = responses.add(responses.GET, url, json={"error": "not found"}, status=404)
        with pytest.raises(FailedRequestError):
            _ = client._get_record_count(endpoint)

    @responses.activate
    def test_get_record_count_invalid_response_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that _get_record_count raises InvalidResponseError for
            non-numeric responses.

        Ensures that when the $count endpoint returns non-numeric data,
        an InvalidResponseError is raised to indicate the response format
        is unexpected.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
        url = build_expected_url(base_url, endpoint, {}, get_count=True)
        _ = responses.add(responses.GET, url, body="not_a_number", status=200)
        with pytest.raises(InvalidResponseError):
            _ = client._get_record_count(endpoint)

    @responses.activate
    def test_get_record_count_with_parameters(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test that _get_record_count works with query parameters for filtered counts.

        Verifies that parameters can be passed to filter the record count,
        allowing for conditional counting based on OData query filters.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
        params = {"filter": "status eq 'active'"}
        url = build_expected_url(base_url, endpoint, params, get_count=True)
        _ = responses.add(responses.GET, url, body="15", status=200)
        count = client._get_record_count(endpoint, params=params)
        assert count == 15


# ============================================================
# Test Dynite client _get_next_page_link Method
# ============================================================
class TestClientGetNextPageLinkMethod:
    """Test cases for the _get_next_page_link private method."""

    def test_get_next_page_link_present(self, client: Dynite, next_link: str) -> None:
        """Test extraction of next page link when present in response.

        Ensures that _get_next_page_link correctly extracts the @odata.nextLink
        value from a JSON response dictionary and returns it as a string.

        Args:
            client (Dynite): Initialized client fixture.
            next_link (str): Sample nextLink URL fixture.
        """
        response = {"@odata.nextLink": next_link}
        extracted_link = client._get_next_page_link(response)
        assert extracted_link == next_link

    def test_get_next_page_link_absent(self, client: Dynite) -> None:
        """Test that _get_next_page_link returns None when no link is present.

        Verifies that when the response does not contain @odata.nextLink,
        the method returns None, indicating no further pages are available.

        Args:
            client (Dynite): Initialized client fixture.
        """
        response = {}
        extracted_link = client._get_next_page_link(response)
        assert extracted_link is None


# ============================================================
# Test Dynite Client get_records Method
# ============================================================
class TestClientGetRecordsMethod:
    """Test cases for the get_records public method."""

    @responses.activate
    def test_get_records_success_handling(
        self, client: Dynite, endpoint: str, base_url: str
    ) -> None:
        """Test successful retrieval of records from an endpoint.

        Verifies that get_records correctly fetches and returns all records
        from a single-page response, including making the necessary $count
        request for total count verification.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
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
        """Test that get_records handles multi-page responses with pagination.

        Ensures that when responses include @odata.nextLink, get_records
        automatically fetches subsequent pages and combines all records
        into a single result list.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
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
        """Test that get_records raises FailedRequestError on HTTP failures.

        Verifies that when the initial request fails, get_records propagates
        the FailedRequestError, ensuring error conditions are not silently
        ignored.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
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
        """Test that get_records raises InvalidResponseError for malformed JSON.

        Ensures that when the API returns invalid JSON, get_records catches
        the JSONDecodeError and raises InvalidResponseError instead,
        providing clear error messaging.

        Args:
            client (Dynite): Initialized client fixture.
            endpoint (str): Sample endpoint fixture.
            base_url (str): Base URL fixture.
        """
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
