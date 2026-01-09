"""
Text processing and formatting utilities.

Provides common text manipulation functions for data cleaning and normalization.
"""

import re


def format_size(size_bytes: float) -> str:
    """
    Convert bytes to human readable string (B, KB, MB, GB, TB).

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string

    Examples:
        >>> format_size(1024)
        '1.00 KB'
        >>> format_size(1536000)
        '1.46 MB'
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace in text by replacing multiple spaces/newlines with single space.

    Args:
        text: Text to normalize

    Returns:
        Normalized text with single spaces and trimmed edges

    Examples:
        >>> normalize_whitespace("  Hello   World  \\n  Test  ")
        'Hello World Test'
    """
    if not text:
        return ""

    # Replace multiple whitespace (including newlines) with single space
    normalized = re.sub(r"\s+", " ", text)

    return normalized.strip()


def normalize_text(text: str, lowercase: bool = False) -> str:
    """
    Comprehensive text normalization.

    Performs:
    - Removes soft hyphens (\\xad)
    - Normalizes whitespace
    - Optionally converts to lowercase

    Args:
        text: Text to normalize
        lowercase: Whether to convert to lowercase

    Returns:
        Normalized text

    Examples:
        >>> normalize_text("Hello\\xad World", lowercase=True)
        'hello world'
    """
    if not text:
        return ""

    # Remove soft hyphens
    normalized = text.replace("\xad", "")

    # Normalize whitespace
    normalized = normalize_whitespace(normalized)

    # Optionally convert to lowercase
    if lowercase:
        normalized = normalized.lower()

    return normalized


def clean_whitespace(text: str) -> str:
    """
    Clean whitespace from text.

    Performs:
    1. Removes leading and trailing whitespace
    2. Replaces multiple consecutive spaces with a single space

    Args:
        text: String to clean

    Returns:
        Cleaned string with normalized whitespace

    Examples:
        >>> clean_whitespace("  Hello    World  ")
        'Hello World'
    """
    if not text or not isinstance(text, str):
        return text

    # Strip leading and trailing whitespace
    text = text.strip()

    # Replace multiple consecutive spaces with single space
    text = re.sub(r"\s+", " ", text)

    return text


def remove_non_alphanumeric(text: str, keep_spaces: bool = True) -> str:
    """
    Remove non-alphanumeric characters from text.

    Args:
        text: Text to clean
        keep_spaces: Whether to keep spaces

    Returns:
        Cleaned text

    Examples:
        >>> remove_non_alphanumeric("Hello, World! 123")
        'Hello World 123'
        >>> remove_non_alphanumeric("Hello, World! 123", keep_spaces=False)
        'HelloWorld123'
    """
    if not text:
        return ""

    if keep_spaces:
        # Keep alphanumeric and spaces
        return re.sub(r"[^a-zA-Z0-9\s]", "", text)
    else:
        # Keep only alphanumeric
        return re.sub(r"[^a-zA-Z0-9]", "", text)


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to specified length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length (including suffix)
        suffix: Suffix to add if truncated

    Returns:
        Truncated text

    Examples:
        >>> truncate_text("This is a very long text", max_length=15)
        'This is a v...'
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix
