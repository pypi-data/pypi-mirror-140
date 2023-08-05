"""Top-level package for interval_search."""

__author__ = """Matthew Andres Moreno"""
__email__ = 'm.more500@gmail.com'
__version__ = '0.1.2'

from .binary_search import binary_search
from .doubling_search import doubling_search

# adapted from https://stackoverflow.com/a/31079085
__all__ = [
    'binary_search',
    'doubling_search',
]
