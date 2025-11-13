"""Dynite - A python client for Business Central OData API.

This module contains the client implementation for interacting with
the Business Central OData API.
"""

import logging

import requests

from .exceptions import InvalidURLError

logger = logging.getLogger(__name__)


class Dynite:
    """Dynite client for Business Central OData API."""

    def __init__(self, base_url: str, auth: tuple[str, str], timeout: int = 30) -> None:
        """Initialize the Dynite client.

        Args:
            base_url (str): The base URL for the Business Central OData API.
            auth (tuple[str, str]): The authentication credentials (username, password).
            timeout (int): The timeout for API requests in seconds.
                Default is 30 seconds.
        """
        self.base_url = self._validate_url(base_url)
        self.session = requests.Session()
        self.session.auth = auth
        self._timeout = timeout

    def _validate_url(self, url: str) -> str:
        """Validate the base URL.

        Args:
            url (str): The base URL to validate.

        Returns:
            str: The validated base URL.
        """
        if not url.startswith(("http://", "https://")):
            msg = f"Invalid URL: {url}"
            logger.exception(msg)
            raise InvalidURLError(msg)
        return url.rstrip("/")
