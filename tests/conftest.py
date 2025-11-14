"""Pytest fixtures for the test suite."""

import pytest

from dynite import Dynite


@pytest.fixture
def auth() -> tuple[str, str]:
    """Provide authentication tuple for tests."""
    return ("user", "pass")


@pytest.fixture
def base_url() -> str:
    """Provide base URL for tests."""
    return "https://example.com/odata"


@pytest.fixture
def endpoint() -> str:
    """Provide endpoint for tests."""
    return "customers"


@pytest.fixture
def client(auth: tuple[str, str], base_url: str) -> Dynite:
    """Provide a Dynite client instance for tests."""

    return Dynite(base_url=base_url, auth=auth)


@pytest.fixture
def next_link() -> str:
    """Provide a sample next link URL for pagination tests."""
    return "https://example.com/odata/customers?$skip=10"
