"""
Text processing utilities.
"""

import re
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)

    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')

    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")

    return text.strip()


def extract_key_terms(text: str, min_length: int = 3) -> list[str]:
    """
    Extract potential key terms from text.

    Simple extraction based on capitalization and patterns.

    Args:
        text: Text to extract terms from
        min_length: Minimum term length

    Returns:
        List of potential key terms
    """
    terms = set()

    # Find capitalized phrases (potential proper nouns/concepts)
    cap_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b'
    for match in re.finditer(cap_pattern, text):
        term = match.group(1)
        if len(term) >= min_length:
            terms.add(term)

    # Find quoted terms
    quote_pattern = r'["\']([^"\']+)["\']'
    for match in re.finditer(quote_pattern, text):
        term = match.group(1).strip()
        if len(term) >= min_length and len(term) < 50:
            terms.add(term)

    # Find bold/emphasized terms (common in slides)
    bold_pattern = r'\*\*([^*]+)\*\*|\*([^*]+)\*'
    for match in re.finditer(bold_pattern, text):
        term = (match.group(1) or match.group(2)).strip()
        if len(term) >= min_length:
            terms.add(term)

    return list(terms)


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences.

    Args:
        text: Text to split

    Returns:
        List of sentences
    """
    # Simple sentence splitting
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def calculate_reading_time(text: str, wpm: int = 200) -> int:
    """
    Calculate estimated reading time in minutes.

    Args:
        text: Text to analyze
        wpm: Words per minute (default 200)

    Returns:
        Estimated minutes to read
    """
    words = len(text.split())
    return max(1, round(words / wpm))


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    # Try to break at word boundary
    truncated = text[:max_length - len(suffix)]
    last_space = truncated.rfind(' ')

    if last_space > max_length // 2:
        truncated = truncated[:last_space]

    return truncated + suffix
