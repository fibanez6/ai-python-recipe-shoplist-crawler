"""
String utility functions for text processing.
"""

import logging
import re

# Get module logger
logger = logging.getLogger(__name__)


def count_chars(text: str) -> int:
    """Return the number of characters in the given text."""
    return len(text)

def count_words(text: str) -> int:
    """Return the number of words in the given text."""
    return len(re.findall(r'\w+', text))

def count_lines(text: str) -> int:
    """Return the number of lines in the given text."""
    if not text:
        return 0
    return text.count("\n") + (0 if text.endswith("\n") else 1)