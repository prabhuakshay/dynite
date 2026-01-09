"""Dynite: A Python client for Microsoft Business Central OData API.

This package provides a simple and efficient client for interacting with the
Microsoft Business Central OData API. It handles authentication, automatic
pagination, retry logic, and error handling to simplify API integration.

Key Features:
- Easy-to-use client for Business Central OData endpoints
- Automatic handling of pagination for large datasets
- Configurable retry logic for transient failures
- Comprehensive error handling with custom exceptions
- Built-in logging support for debugging and monitoring
- Type hints for better IDE support and code clarity

Quick Start:
    from dynite import Dynite

    client = Dynite(
        base_url="https://api.businesscentral.dynamics.com/v2.0/tenant_id/api/v2.0",
        auth=("username", "password")
    )
    companies = client.get_records("companies")

For detailed usage examples, installation instructions, and API documentation,
please refer to the README.md file.

Version: 0.1.0
"""

import logging
from warnings import warn

from .client import Dynite

# Warn users to use a different library
__version__ = "0.1.0"

# Configure default logging for the package
# This prevents "No handler found" warnings when users don't configure logging
# Users can override this by configuring their own handlers on the 'dynite' logger
logging.getLogger(__name__).addHandler(logging.NullHandler())


# Expose the main client class in the package's public API
# This allows users to import directly: from dynite import Dynite
__all__ = ["Dynite"]


warn("dynite is deprecated, use odyn instead", DeprecationWarning, stacklevel=2)
