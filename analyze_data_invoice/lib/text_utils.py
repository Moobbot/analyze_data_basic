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
        Normalized text
    """
    if not text:
        return ""

    # Replace multiple whitespace (including newlines) with single space
    normalized = re.sub(r"\s+", " ", text)

    return normalized.strip()


def normalize_text(text: str, lowercase: bool = False) -> str:
    """
    Comprehensive text normalization.

    Args:
        text: Text to normalize
        lowercase: Whether to convert to lowercase

    Returns:
        Normalized text
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


def remove_non_alphanumeric(text: str, keep_spaces: bool = True) -> str:
    """
    Remove non-alphanumeric characters from text.

    Args:
        text: Text to clean
        keep_spaces: Whether to keep spaces

    Returns:
        Cleaned text
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
    """
    if not text or len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix
