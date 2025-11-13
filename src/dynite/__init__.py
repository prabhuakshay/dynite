"""Dynite - A python client for Business Central OData API."""

import logging

__version__ = "0.1.0"

# Set up a default logger for the package
# Users of the library can configure logging as needed
logging.getLogger(__name__).addHandler(logging.NullHandler())
