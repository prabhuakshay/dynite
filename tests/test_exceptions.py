"""Test Dynite.exceptions classes."""

import pytest

from dynite.exceptions import (
    DyniteError,
    FailedRequestError,
    InvalidResponseError,
    InvalidURLError,
)


class TestDyniteExceptions:
    def test_dynite_error_inherits_exception(self) -> None:
        """Test that DyniteError inherits from Exception."""
        assert issubclass(DyniteError, Exception)

    def test_failed_request_error_inherits_dynite_error(self) -> None:
        """Test that FailedRequestError inherits from DyniteError."""
        assert issubclass(FailedRequestError, DyniteError)

    def test_invalid_response_error_inherits_dynite_error(self) -> None:
        """Test that InvalidResponseError inherits from DyniteError."""
        assert issubclass(InvalidResponseError, DyniteError)

    def test_invalid_url_error_inherits_dynite_error(self) -> None:
        """Test that InvalidURLError inherits from DyniteError."""
        assert issubclass(InvalidURLError, DyniteError)

    def test_failed_request_error_message(self) -> None:
        """Test the message of FailedRequestError."""
        error_message = "Request failed"
        with pytest.raises(FailedRequestError, match=error_message):
            raise FailedRequestError(error_message)

    def test_invalid_response_error_message(self) -> None:
        """Test the message of InvalidResponseError."""
        error_message = "Invalid response"
        with pytest.raises(InvalidResponseError, match=error_message):
            raise InvalidResponseError(error_message)

    def test_invalid_url_error_message(self) -> None:
        """Test the message of InvalidURLError."""
        error_message = "Invalid URL"
        with pytest.raises(InvalidURLError, match=error_message):
            raise InvalidURLError(error_message)

    def test_dynite_error_message(self) -> None:
        """Test the message of DyniteError."""
        error_message = "General Dynite error"
        with pytest.raises(DyniteError, match=error_message):
            raise DyniteError(error_message)
