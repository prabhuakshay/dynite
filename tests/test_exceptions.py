"""Test suite for Dynite exception classes.

This module contains comprehensive tests for all custom exception classes
defined in the Dynite library. It verifies inheritance relationships, error
message handling, and proper exception raising behavior. These tests ensure
that the exception hierarchy works correctly and that exceptions can be
caught and handled appropriately in user code.

Tests cover:
- Inheritance from base Exception and DyniteError classes
- Exception message propagation and matching
- Proper exception types for different error scenarios
"""

import pytest

from dynite.exceptions import (
    DyniteError,
    FailedRequestError,
    InvalidResponseError,
    InvalidURLError,
)


class TestDyniteExceptions:
    """Test cases for Dynite exception class hierarchy and behavior."""

    def test_dynite_error_inherits_exception(self) -> None:
        """Test that DyniteError properly inherits from the base Exception class.

        Verifies the fundamental inheritance relationship that allows DyniteError
        to be caught as a standard Python exception. This ensures compatibility
        with general exception handling patterns.
        """
        assert issubclass(DyniteError, Exception)

    def test_failed_request_error_inherits_dynite_error(self) -> None:
        """Test that FailedRequestError inherits from DyniteError.

        Ensures that FailedRequestError is part of the Dynite exception hierarchy,
        allowing users to catch all Dynite errors with a single DyniteError except
        clause, or catch specific request failures separately.
        """
        assert issubclass(FailedRequestError, DyniteError)

    def test_invalid_response_error_inherits_dynite_error(self) -> None:
        """Test that InvalidResponseError inherits from DyniteError.

        Confirms that InvalidResponseError follows the Dynite exception hierarchy,
        enabling consistent error handling for API response parsing issues.
        """
        assert issubclass(InvalidResponseError, DyniteError)

    def test_invalid_url_error_inherits_dynite_error(self) -> None:
        """Test that InvalidURLError inherits from DyniteError.

        Validates that InvalidURLError is properly integrated into the exception
        hierarchy, allowing for unified error handling of URL validation errors.
        """
        assert issubclass(InvalidURLError, DyniteError)

    def test_failed_request_error_message(self) -> None:
        """Test that FailedRequestError preserves and displays error messages correctly.

        Verifies that when a FailedRequestError is raised with a specific message,
        that message is properly stored and can be matched in exception handling.
        This ensures informative error reporting for request failures.
        """
        error_message = "Request failed"
        with pytest.raises(FailedRequestError, match=error_message):
            raise FailedRequestError(error_message)

    def test_invalid_response_error_message(self) -> None:
        """Test that InvalidResponseError handles error messages properly.

        Ensures that InvalidResponseError instances correctly store and expose
        the error message provided during instantiation, enabling clear error
        communication for response parsing failures.
        """
        error_message = "Invalid response"
        with pytest.raises(InvalidResponseError, match=error_message):
            raise InvalidResponseError(error_message)

    def test_invalid_url_error_message(self) -> None:
        """Test that InvalidURLError correctly manages error messages.

        Confirms that InvalidURLError preserves the message passed to it,
        allowing users to understand what made the URL invalid when the
        exception is raised during client initialization.
        """
        error_message = "Invalid URL"
        with pytest.raises(InvalidURLError, match=error_message):
            raise InvalidURLError(error_message)

    def test_dynite_error_message(self) -> None:
        """Test that DyniteError base class handles messages correctly.

        Verifies that the base DyniteError class properly stores and exposes
        error messages, providing a foundation for all derived exception types
        to maintain consistent message handling behavior.
        """
        error_message = "General Dynite error"
        with pytest.raises(DyniteError, match=error_message):
            raise DyniteError(error_message)
