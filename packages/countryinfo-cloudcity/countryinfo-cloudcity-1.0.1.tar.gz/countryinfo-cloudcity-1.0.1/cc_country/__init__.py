from .country import CountryInfo
from .exceptions import (
    CountryNotFoundError
)

# Set default logging handler to avoid "No handler found" warnings.
import logging
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
