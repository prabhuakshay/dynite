"""Dynite - A Python client for Microsoft Business Central OData API.

This module provides a comprehensive and efficient client for interacting with the
Microsoft Business Central OData API. It simplifies API integration by handling
authentication, automatic pagination, retry logic, error handling, and response
parsing. The client is designed to be robust, configurable, and easy to use for
developers building applications that need to access Business Central data.

Key Features:
- Automatic handling of OData pagination for large datasets.
- Configurable retry logic for transient failures.
- Comprehensive error handling with custom exceptions.
- Support for query parameters and filtering.
- Logging integration for debugging and monitoring.

Dependencies:
- requests: For HTTP requests.
- urllib3: For retry strategies.
- Standard library modules: json, logging, typing, urllib.parse.

Usage:
    from dynite import Dynite

    client = Dynite(
        base_url="https://api.businesscentral.dynamics.com/v2.0/tenant_id/api/v2.0",
        auth=("username", "password")
    )
    records = client.get_records("companies")

For more detailed usage examples, installation instructions, and API documentation,
please refer to the README.md file.
"""

import logging
from json import JSONDecodeError
from typing import Any
from urllib.parse import urlencode, urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .exceptions import FailedRequestError, InvalidResponseError, InvalidURLError

logger = logging.getLogger(__name__)


class Dynite:
    """A client for interacting with the Microsoft Business Central OData API.

    This class encapsulates all the functionality needed to communicate with the
    Business Central OData API, including authentication, request handling, and
    data retrieval. It provides a high-level interface for fetching records from
    various endpoints, handling pagination automatically, and managing errors
    gracefully.

    Attributes:
        DEFAULT_TIMEOUT (int): The default timeout for API requests in seconds (30).
        DEFAULT_RETRIES (int): The default number of retries for failed requests (3).
        base_url (str): The validated base URL for the API.
        session (requests.Session): The HTTP session used for making requests.
        _timeout (int): The configured timeout for requests.
    """

    DEFAULT_TIMEOUT = 30
    DEFAULT_RETRIES = 3

    def __init__(
        self,
        base_url: str,
        auth: tuple[str, str],
        timeout: int = DEFAULT_TIMEOUT,
        retries: int = DEFAULT_RETRIES,
    ) -> None:
        """Initialize the Dynite client with configuration parameters.

        Sets up the client with the necessary authentication and session
        configuration for making requests to the Business Central OData API.
        Validates the provided base URL and timeout, configures retry logic,
        and establishes an authenticated session.

        Args:
            base_url (str): The base URL for the Business Central OData API.
                Must be a valid HTTP or HTTPS URL pointing to the API endpoint.
                Example: "https://api.businesscentral.dynamics.com/v2.0/tenant_id/api/v2.0"
            auth (tuple[str, str]): A tuple containing the authentication credentials
                in the format (username, password). These are used for basic
                authentication with the API.
            timeout (int, optional): The timeout in seconds for individual API
                requests. If <= 0, defaults to DEFAULT_TIMEOUT (30 seconds).
                Defaults to DEFAULT_TIMEOUT.
            retries (int, optional): The number of times to retry failed requests
                due to transient errors (e.g., 429, 5xx status codes). If < 0,
                defaults to DEFAULT_RETRIES (3). Defaults to DEFAULT_RETRIES.

        Raises:
            InvalidURLError: If the provided base_url is not a valid URL.
        """
        self.base_url = self._validate_url(base_url)
        self.session = requests.Session()
        self.session.auth = auth
        self._timeout = self._validate_timeout(timeout)
        self._mount_adapters(retries)
        logger.debug("Dynite client initialized.")

    def _validate_url(self, url: str) -> str:
        """Validate and normalize the base URL for the API.

        Ensures that the provided URL is a valid HTTP or HTTPS URL with a proper
        network location (netloc). Strips leading/trailing whitespace and trailing
        slashes for consistency. This method is crucial for preventing connection
        errors due to malformed URLs.

        Args:
            url (str): The base URL string to validate. Should be a complete
                HTTP or HTTPS URL pointing to the Business Central API.

        Returns:
            str: The validated and normalized URL, with trailing slashes removed.

        Raises:
            InvalidURLError: If the URL does not start with 'http://' or 'https://',
                or if it lacks a valid network location (domain/host).
        """
        url = url.strip()
        if not url.startswith(("http://", "https://")):
            msg = f"Invalid URL: {url}"
            logger.error(msg)
            raise InvalidURLError(msg)
        parsed = urlparse(url)
        if not parsed.netloc:
            msg = f"Invalid URL: {url}"
            logger.error(msg)
            raise InvalidURLError(msg)
        return url.rstrip("/")

    def _validate_timeout(self, timeout: int) -> int:
        """Validate and adjust the timeout value for API requests.

        Ensures that the timeout is a positive integer. If an invalid (non-positive)
        value is provided, logs a warning and falls back to the default timeout.
        This prevents indefinite hangs on network requests.

        Args:
            timeout (int): The proposed timeout value in seconds. Should be > 0.

        Returns:
            int: The validated timeout value, either the provided value or the
                default if invalid.
        """
        if timeout <= 0:
            logger.warning(
                "Invalid timeout value: %s. Using default timeout of %s seconds.",
                timeout,
                self.DEFAULT_TIMEOUT,
            )
            return self.DEFAULT_TIMEOUT
        return timeout

    def _mount_adapters(self, retries: int) -> None:
        """Configure HTTP adapters with a retry strategy for the session.

        Sets up retry logic for transient HTTP errors to improve reliability.
        Uses urllib3's Retry class to handle specific status codes and methods.
        Applies the retry strategy to both HTTP and HTTPS adapters.

        Args:
            retries (int): The number of retries for failed requests. If negative,
                defaults to DEFAULT_RETRIES. Only GET requests are retried for
                safety.

        Returns:
            None
        """
        # Validate retries
        if retries < 0:
            logger.warning(
                "Invalid retries value: %s. Using default retries of %s.",
                retries,
                self.DEFAULT_RETRIES,
            )
            retries = self.DEFAULT_RETRIES
        # Set up retry strategy
        retry_strategy = Retry(
            total=retries,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            backoff_factor=1,
        )
        # Mount adapters with the retry strategy
        self.session.mount("http://", HTTPAdapter(max_retries=retry_strategy))
        self.session.mount("https://", HTTPAdapter(max_retries=retry_strategy))

    def _build_url(
        self,
        endpoint: str,
        params: dict[str, str] | None = None,
        *,
        get_count: bool = False,
    ) -> str:
        """Construct the complete URL for an API endpoint with optional parameters.

        Builds a full URL by combining the base URL, endpoint, and query parameters.
        Supports appending '/$count' for OData count queries. Ensures proper URL
        encoding of parameters and handles leading slashes on endpoints.

        Args:
            endpoint (str): The API endpoint path, e.g., "companies" or "salesOrders".
                Leading slashes are automatically stripped.
            params (dict[str, str] | None, optional): A dictionary of query parameters
                to append to the URL. Keys and values should be strings.
                Defaults to None.
            get_count (bool, optional): If True, appends '/$count' to the endpoint
                for retrieving record counts via OData. Defaults to False.

        Returns:
            str: The fully constructed URL, including base URL, endpoint, and encoded
                query parameters if provided.
        """
        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{endpoint}"

        if get_count:
            url = f"{url}/$count"

        if params:
            query_string = urlencode(params)
            url = f"{url}?{query_string}"
        logger.debug("Built URL: %s", url)
        return url

    def _get(self, url: str) -> requests.Response:
        """Perform a GET request to the specified URL with error handling.

        Executes an HTTP GET request using the configured session, which includes
        authentication, timeout, and retry logic. Raises an exception for any
        request failures to ensure robust error handling.

        Args:
            url (str): The complete URL to send the GET request to, typically
                constructed by _build_url.

        Returns:
            requests.Response: The HTTP response object if the request succeeds.
                The response will have a successful status code (2xx).

        Raises:
            FailedRequestError: If the request fails due to network issues,
                timeouts, or non-2xx status codes. The original exception is
                chained for debugging.
        """
        try:
            response = self.session.get(url, timeout=self._timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            msg = f"Failed to perform GET request: {e}"
            logger.exception(msg)
            raise FailedRequestError(msg) from e
        logger.debug("GET request successful: %s", url)
        return response

    def _get_record_count(
        self, endpoint: str, params: dict[str, str] | None = None
    ) -> int:
        """Retrieve the total number of records available at an endpoint.

        Makes a specialized GET request to the OData $count endpoint to get the
        total record count without fetching the actual data. This is essential
        for pagination and progress tracking when retrieving large datasets.
        Handles UTF-8 BOM stripping and validates that the response is numeric.

        Args:
            endpoint (str): The API endpoint for which to count records, e.g.,
                "companies".
            params (dict[str, str] | None, optional): Query parameters to filter
                the count, such as date ranges or filters. Defaults to None.

        Returns:
            int: The total number of records available at the endpoint, after
                applying any provided filters.

        Raises:
            InvalidResponseError: If the response is not a valid numeric string.
            FailedRequestError: If the underlying GET request fails.
        """
        url = self._build_url(endpoint, params, get_count=True)

        response = self._get(url)

        # Decode bytes explicitly as UTF-8 and strip BOM if present
        clean_text = response.content.decode("utf-8-sig").strip()

        if not clean_text.isdigit():
            msg = f"Invalid response for record count: {clean_text}"
            logger.error(msg)
            raise InvalidResponseError(msg)

        logger.debug("Total record count retrieved: %s", clean_text)
        return int(clean_text)

    def _get_next_page_link(self, response: dict[str, Any]) -> str | None:
        """Extract the OData next page link from a JSON response.

        Parses the response dictionary for the '@odata.nextLink' key, which
        indicates if there are more pages of data available. This is part of
        OData's pagination mechanism for handling large result sets.

        Args:
            response (dict[str, Any]): The parsed JSON response from an API
                request, expected to be a dictionary containing OData metadata.

        Returns:
            str | None: The URL for the next page of results if available,
                otherwise None. The link can be used directly for subsequent
                requests.
        """
        next_link = response.get("@odata.nextLink")
        return str(next_link) if next_link else None

    def get_records(
        self, endpoint: str, params: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        """Retrieve all records from a specified API endpoint with automatic pagination.

        Fetches records from the Business Central OData API, handling pagination
        transparently by following '@odata.nextLink' until all records are retrieved.
        First obtains the total count for logging and progress tracking. Supports
        query parameters for filtering, sorting, and limiting results.

        Args:
            endpoint (str): The API endpoint to query, e.g., "companies",
                "customers", or "salesOrders". Should correspond to a valid
                OData entity set.
            params (dict[str, str] | None, optional): Query parameters for the
                request, such as $filter, $orderby, $top, etc. Keys and values
                must be strings. Defaults to None.

        Returns:
            list[dict[str, Any]]: A list of dictionaries representing the records.
                Each dictionary contains the fields and values for one record.
                The list includes all records across all pages.

        Raises:
            InvalidResponseError: If the API returns invalid JSON or unexpected
                response format.
            FailedRequestError: If any of the underlying HTTP requests fail.
        """
        total_records = self._get_record_count(endpoint, params)
        logger.debug("Total records to retrieve: %s", total_records)

        url = self._build_url(endpoint, params)

        records: list[dict[str, Any]] = []

        # Paginate through all available records using OData nextLink
        while True:
            response = self._get(url)
            try:
                json_response = response.json()
            except JSONDecodeError as e:
                msg = f"Invalid JSON response: {e}"
                logger.exception(msg)
                raise InvalidResponseError(msg) from e
            records.extend(json_response.get("value", []))

            next_link = self._get_next_page_link(json_response)
            if not next_link:
                break
            url = next_link
            logger.debug("Loaded %d of %d records so far.", len(records), total_records)

        logger.debug("Total records retrieved: %d", len(records))

        return records
