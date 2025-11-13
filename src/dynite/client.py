"""Dynite - A python client for Business Central OData API.

This module contains the client implementation for interacting with
the Business Central OData API.
"""

import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .exceptions import InvalidURLError

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

    def _validate_url(self, url: str) -> str:
        """Validate the base URL.

        Args:
            url (str): The base URL to validate.

        Returns:
            str: The validated base URL.
        """
        if not url.startswith(("http://", "https://")):
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
