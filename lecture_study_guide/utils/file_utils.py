"""
File handling utilities.
"""

from pathlib import Path
from typing import Optional


def ensure_dir(path: str | Path) -> Path:
    """
    Ensure directory exists, creating if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_type(path: str | Path) -> Optional[str]:
    """
    Get the type of lecture file.

    Args:
        path: File path

    Returns:
        File type ('pptx', 'pdf', or None if unsupported)
    """
    path = Path(path)
    ext = path.suffix.lower()

    type_map = {
        '.pptx': 'pptx',
        '.ppt': 'pptx',
        '.pdf': 'pdf',
    }

    return type_map.get(ext)


def is_supported_file(path: str | Path) -> bool:
    """Check if file type is supported."""
    return get_file_type(path) is not None


def get_output_filename(
    input_path: str | Path,
    suffix: str,
    extension: str
) -> str:
    """
    Generate output filename based on input file.

    Args:
        input_path: Original input file path
        suffix: Suffix to add (e.g., '_study_guide')
        extension: Output file extension (e.g., '.md')

    Returns:
        Output filename
    """
    stem = Path(input_path).stem
    if not extension.startswith('.'):
        extension = '.' + extension
    return f"{stem}{suffix}{extension}"
