"""Custom exceptions for the Dynite library.

This module defines custom exception classes used in the Dynite library
to handle various error scenarios.
"""


class DyniteError(Exception):
    """Base exception class for Dynite errors."""


class InvalidURLError(DyniteError):
    """Exception raised for invalid Base URLs."""
