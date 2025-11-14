"""Dynite - A python client for Business Central OData API.

This module contains the client implementation for interacting with
the Business Central OData API.
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
    """Dynite client for Business Central OData API."""

    def __init__(
        self, base_url: str, auth: tuple[str, str], timeout: int = 30, retries: int = 3
    ) -> None:
        """Initialize the Dynite client.

        Args:
            base_url (str): The base URL for the Business Central OData API.
            auth (tuple[str, str]): The authentication credentials (username, password).
            timeout (int): The timeout for API requests in seconds.
                Default is 30 seconds.
            retries (int): The number of retries for failed requests.
                Default is 3 retries.
        """
        self.base_url = self._validate_url(base_url)
        self.session = requests.Session()
        self.session.auth = auth
        self._timeout = self._validate_timeout(timeout)
        self._mount_adapters(retries)
        logger.debug("Dynite client initialized.")

    def _validate_url(self, url: str) -> str:
        """Validate the base URL.

        Args:
            url (str): The base URL to validate.

        Returns:
            str: The validated base URL.
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
        """Validate the timeout value.

        Args:
            timeout (int): The timeout value to validate.

        Returns:
            int: The validated timeout value.
        """
        if timeout <= 0:
            msg = (
                f"Invalid timeout value: {timeout}. "
                f"Using default timeout of 30 seconds."
            )
            logger.warning(msg)
            return 30
        return timeout

    def _mount_adapters(self, retries: int) -> None:
        """Mount HTTP adapters with retry strategy.

        Args:
            retries (int): The number of retries for failed requests.

        Returns:
            None
        """
        # Validate retries
        if retries < 0:
            msg = f"Invalid retries value: {retries}. Using default retries of 3."
            logger.warning(msg)
            retries = 3
        # Set up retry strategy
        retry_strategy = Retry(
            total=retries,
            status_forcelist=[429, 500, 502, 503, 504],
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
        """Build the full URL for an API endpoint.

        Args:
            endpoint (str): The API endpoint.
            params (dict[str, str] | None): Optional query parameters.
            get_count (bool): Flag to indicate if the URL is for getting record count.

        Returns:
            str: The full URL for the API endpoint.
        """
        endpoint = endpoint.lstrip("/")
        url = f"{self.base_url}/{endpoint}"

        if get_count:
            url = f"{url}/$count"

        if params:
            query_string = urlencode(params)
            url = f"{url}?{query_string}"
        msg = f"Built URL: {url}"
        logger.debug(msg)
        return url

    def _get(self, url: str) -> requests.Response:
        """Perform a GET request to the specified URL.

        Args:
            url (str): The URL to send the GET request to.

        Returns:
            requests.Response: The response object from the GET request.

        Raises:
            FailedRequestError: If the API request fails.
        """
        try:
            response = self.session.get(url, timeout=self._timeout)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            msg = f"Failed to perform GET request: {e}"
            logger.exception(msg)
            raise FailedRequestError(msg) from e
        msg = f"GET request successful: {url}"
        logger.debug(msg)
        return response

    def _get_record_count(
        self, endpoint: str, params: dict[str, str] | None = None
    ) -> int:
        """Get total record count from a given endpoint.

        Args:
            endpoint (str): The API endpoint.
            params (dict[str, str] | None): Optional query parameters.

        Returns:
            int: The total record count.

        Raises:
            InvalidResponseError: If the API response is invalid.
            FailedRequestError: If the API request fails.
        """
        url = self._build_url(endpoint, params, get_count=True)

        response = self._get(url)

        # Decode bytes explicitly as UTF-8 and strip BOM if present
        clean_text = response.content.decode("utf-8-sig").strip()

        if not clean_text.isdigit():
            msg = f"Invalid response for record count: {clean_text}"
            logger.error(msg)
            raise InvalidResponseError(msg)

        msg = f"Total record count retrieved: {clean_text}"
        logger.debug(msg)
        return int(clean_text)

    def _get_next_page_link(self, response: dict[str, Any]) -> str | None:
        """Extract the next page link from the response body.

        Args:
            response (requests.Response): The response object from an API request.

        Returns:
            str | None: The next page link if available, otherwise None.
        """
        next_link = response.get("@odata.nextLink")
        return str(next_link) if next_link else None

    def get_records(
        self, endpoint: str, params: dict[str, str] | None = None
    ) -> list[dict[str, Any]]:
        """Get records from a given endpoint.

        Args:
            endpoint (str): The API endpoint.
            params (dict[str, str] | None): Optional query parameters.

        Returns:
            list[dict[str, Any]]: A list of records retrieved from the endpoint.

        Raises:
            InvalidResponseError: If the API response is invalid.
            FailedRequestError: If the API request fails.
        """
        total_records = self._get_record_count(endpoint, params)
        msg = f"Total records to retrieve: {total_records}"
        logger.debug(msg)

        url = self._build_url(endpoint, params)

        records: list[dict[str, Any]] = []

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
            msg = f"Loaded {len(records)} of {total_records} records so far."
            logger.debug(msg)

        msg = f"Total records retrieved: {len(records)}"
        logger.debug(msg)

        return records
