"""Custom exceptions for the Dynite library.

This module defines a hierarchy of custom exception classes specifically designed
for the Dynite library. These exceptions provide clear, descriptive error messages
and allow for precise error handling when interacting with the Microsoft Business
Central OData API. All exceptions inherit from the base DyniteError class,
enabling users to catch all Dynite-related errors with a single except clause.

Exception Hierarchy:
- DyniteError: Base exception for all Dynite errors.
  - InvalidURLError: For malformed or invalid base URLs.
  - InvalidResponseError: For unexpected or malformed API responses.
  - FailedRequestError: For network or HTTP request failures.

Usage:
    try:
        client = Dynite("invalid-url", ("user", "pass"))
    except InvalidURLError as e:
        print(f"URL error: {e}")

This design allows for granular error handling while maintaining simplicity.
"""


class DyniteError(Exception):
    """Base exception class for all Dynite-related errors.

    This is the root exception class in the Dynite exception hierarchy. All
    other Dynite exceptions inherit from this class, allowing users to catch
    any Dynite error by catching DyniteError. It provides a consistent base
    for error handling across the library.

    Inherits from the built-in Exception class, so it supports all standard
    exception features like message passing and chaining.
    """


class InvalidURLError(DyniteError):
    """Exception raised when an invalid base URL is provided.

    This exception is thrown during client initialization when the provided
    base URL for the Business Central OData API does not meet the required
    criteria. The URL must be a valid HTTP or HTTPS URL with a proper
    network location (domain/host).

    Common causes:
    - URLs not starting with 'http://' or 'https://'
    - Malformed URLs without a valid domain
    - Empty or whitespace-only strings

    Example:
        try:
            client = Dynite("ftp://invalid", ("user", "pass"))
        except InvalidURLError:
            # Handle invalid URL
            pass
    """


class InvalidResponseError(DyniteError):
    """Exception raised when the API returns an invalid or unexpected response.

    This exception occurs when the Business Central OData API returns a response
    that cannot be properly parsed or does not match the expected format. This
    includes JSON decoding errors, missing required fields, or unexpected data
    types in the response.

    Common causes:
    - Malformed JSON in the API response
    - Missing '@odata.nextLink' or 'value' fields in paginated responses
    - Non-numeric responses from $count endpoints
    - Unexpected response structure changes from the API

    Example:
        try:
            records = client.get_records("companies")
        except InvalidResponseError:
            # Handle response parsing issues
            pass
    """


class FailedRequestError(DyniteError):
    """Exception raised when an API request fails due to network or HTTP issues.

    This exception is thrown when HTTP requests to the Business Central OData API
    encounter errors that prevent successful completion. This includes network
    timeouts, connection failures, authentication issues, and HTTP error status
    codes (after retries are exhausted).

    Common causes:
    - Network connectivity problems
    - Authentication failures (invalid credentials)
    - Server-side errors (5xx status codes)
    - Rate limiting (429 status codes)
    - Request timeouts
    - DNS resolution failures

    Note: Transient errors like 429 and 5xx codes are automatically retried
    according to the client's retry configuration before raising this exception.

    Example:
        try:
            records = client.get_records("companies")
        except FailedRequestError:
            # Handle network or HTTP errors
            pass
    """
