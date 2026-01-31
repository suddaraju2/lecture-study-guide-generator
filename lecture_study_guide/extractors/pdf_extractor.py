"""
PDF content extractor for lecture slides and documents.
"""

import re
from pathlib import Path
from typing import Optional

from .base import BaseExtractor, ExtractedContent


class PDFExtractor(BaseExtractor):
    """Extract content from PDF files."""

    SUPPORTED_EXTENSIONS = [".pdf"]

    def extract(self) -> ExtractedContent:
        """
        Extract content from PDF file.

        Uses pypdf as primary, falls back to pdfplumber for advanced features.
        """
        # Try pypdf first (more reliable)
        try:
            return self._extract_with_pypdf()
        except ImportError:
            pass

        # Fall back to pdfplumber
        try:
            return self._extract_with_pdfplumber()
        except ImportError:
            raise ImportError(
                "PDF extraction requires pypdf or pdfplumber. "
                "Install with: pip install pypdf"
            )

    def _extract_with_pypdf(self) -> ExtractedContent:
        """Extract using pypdf library."""
        from pypdf import PdfReader

        reader = PdfReader(str(self.file_path))

        slides = []
        all_text = []
        tables = []
        images = []

        metadata = {
            "title": reader.metadata.title if reader.metadata else "",
            "author": reader.metadata.author if reader.metadata else "",
            "subject": reader.metadata.subject if reader.metadata else "",
            "creator": reader.metadata.creator if reader.metadata else "",
            "page_count": len(reader.pages),
        }

        for page_num, page in enumerate(reader.pages, 1):
            page_text = page.extract_text() or ""

            title = self._extract_title(page_text)
            body = self._extract_body(page_text, title)

            slide_content = {
                "number": page_num,
                "title": title,
                "content": page_text.strip(),
                "body": body,
                "notes": "",
                "has_table": False,
                "has_image": len(page.images) > 0 if hasattr(page, 'images') else False,
            }

            slides.append(slide_content)
            all_text.append(page_text)

            # Track images
            if hasattr(page, 'images'):
                for img in page.images:
                    images.append({
                        "page_number": page_num,
                        "name": getattr(img, 'name', ''),
                    })

        return ExtractedContent(
            raw_text="\n\n".join(all_text),
            slides=slides,
            tables=tables,
            images=images,
            metadata=metadata,
            source_file=str(self.file_path)
        )

    def _extract_with_pdfplumber(self) -> ExtractedContent:
        """Extract using pdfplumber library (better for tables)."""
        import pdfplumber

        slides = []
        all_text = []
        tables = []
        images = []

        with pdfplumber.open(str(self.file_path)) as pdf:
            metadata = self._extract_metadata_plumber(pdf)

            for page_num, page in enumerate(pdf.pages, 1):
                page_text = page.extract_text() or ""

                title = self._extract_title(page_text)
                body = self._extract_body(page_text, title)

                slide_content = {
                    "number": page_num,
                    "title": title,
                    "content": page_text.strip(),
                    "body": body,
                    "notes": "",
                    "has_table": False,
                    "has_image": False,
                }

                # Extract tables
                page_tables = page.extract_tables()
                if page_tables:
                    slide_content["has_table"] = True
                    for table in page_tables:
                        if table and any(any(cell for cell in row) for row in table):
                            cleaned_table = [
                                [str(cell).strip() if cell else "" for cell in row]
                                for row in table
                            ]
                            tables.append(cleaned_table)

                # Check for images
                if page.images:
                    slide_content["has_image"] = True
                    for img in page.images:
                        images.append({
                            "page_number": page_num,
                            "x0": img.get("x0"),
                            "y0": img.get("y0"),
                        })

                slides.append(slide_content)
                all_text.append(page_text)

        return ExtractedContent(
            raw_text="\n\n".join(all_text),
            slides=slides,
            tables=tables,
            images=images,
            metadata=metadata,
            source_file=str(self.file_path)
        )

    def _extract_metadata_plumber(self, pdf) -> dict:
        """Extract metadata from pdfplumber PDF object."""
        meta = pdf.metadata or {}
        return {
            "title": meta.get("Title", "") or "",
            "author": meta.get("Author", "") or "",
            "subject": meta.get("Subject", "") or "",
            "creator": meta.get("Creator", "") or "",
            "created": meta.get("CreationDate", "") or "",
            "modified": meta.get("ModDate", "") or "",
            "page_count": len(pdf.pages),
        }

    def _extract_title(self, page_text: str) -> str:
        """
        Attempt to extract the slide title from page text.

        Heuristics:
        - First non-empty line is often the title
        - Title is usually short (< 100 chars)
        """
        lines = [line.strip() for line in page_text.split('\n') if line.strip()]
        if not lines:
            return ""

        # First line is usually the title
        first_line = lines[0]

        # If first line is too long, it might be body text
        if len(first_line) > 100:
            return ""

        return first_line

    def _extract_body(self, page_text: str, title: str) -> str:
        """Extract body text (everything except the title)."""
        if not title:
            return page_text.strip()

        # Remove the title from the beginning
        body = page_text.strip()
        if body.startswith(title):
            body = body[len(title):].strip()

        return body

