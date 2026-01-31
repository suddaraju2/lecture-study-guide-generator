"""
Base extractor interface for content extraction.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class ExtractedContent:
    """Container for extracted lecture content."""
    raw_text: str
    slides: list[dict]  # List of slide content with metadata
    tables: list[list[list[str]]]  # Extracted tables
    images: list[dict]  # Image metadata and paths
    metadata: dict  # Document metadata
    source_file: str

    @property
    def slide_count(self) -> int:
        """Get the number of slides/pages."""
        return len(self.slides)

    def get_slide_text(self, slide_num: int) -> Optional[str]:
        """Get text content for a specific slide (1-indexed)."""
        if 1 <= slide_num <= len(self.slides):
            return self.slides[slide_num - 1].get("content", "")
        return None

    def get_all_text(self) -> str:
        """Get all text content combined."""
        return "\n\n".join(
            f"=== Slide {s.get('number', i+1)} ===\n{s.get('content', '')}"
            for i, s in enumerate(self.slides)
        )


class BaseExtractor(ABC):
    """Abstract base class for content extractors."""

    SUPPORTED_EXTENSIONS: list[str] = []

    def __init__(self, file_path: str | Path):
        """
        Initialize extractor with file path.

        Args:
            file_path: Path to the lecture file
        """
        self.file_path = Path(file_path)
        self._validate_file()

    def _validate_file(self) -> None:
        """Validate the file exists and has correct extension."""
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        ext = self.file_path.suffix.lower()
        if ext not in self.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Unsupported file type: {ext}. "
                f"Supported: {', '.join(self.SUPPORTED_EXTENSIONS)}"
            )

    @abstractmethod
    def extract(self) -> ExtractedContent:
        """
        Extract content from the lecture file.

        Returns:
            ExtractedContent object containing all extracted information
        """
        pass

    @classmethod
    def can_handle(cls, file_path: str | Path) -> bool:
        """Check if this extractor can handle the given file."""
        ext = Path(file_path).suffix.lower()
        return ext in cls.SUPPORTED_EXTENSIONS
