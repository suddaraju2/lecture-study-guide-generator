"""Tests for content extractors."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from lecture_study_guide.extractors.base import BaseExtractor, ExtractedContent
from lecture_study_guide.extractors.pdf_extractor import PDFExtractor
from lecture_study_guide.extractors.pptx_extractor import PowerPointExtractor


class TestExtractedContent:
    """Tests for ExtractedContent class."""

    def test_slide_count(self):
        """Test slide count property."""
        content = ExtractedContent(
            raw_text="test",
            slides=[{"number": 1}, {"number": 2}],
            tables=[],
            images=[],
            metadata={},
            source_file="test.pdf"
        )
        assert content.slide_count == 2

    def test_get_slide_text(self):
        """Test getting text for specific slide."""
        content = ExtractedContent(
            raw_text="test",
            slides=[
                {"number": 1, "content": "Slide 1 content"},
                {"number": 2, "content": "Slide 2 content"}
            ],
            tables=[],
            images=[],
            metadata={},
            source_file="test.pdf"
        )
        assert content.get_slide_text(1) == "Slide 1 content"
        assert content.get_slide_text(2) == "Slide 2 content"
        assert content.get_slide_text(3) is None

    def test_get_all_text(self):
        """Test getting all text combined."""
        content = ExtractedContent(
            raw_text="test",
            slides=[
                {"number": 1, "content": "First"},
                {"number": 2, "content": "Second"}
            ],
            tables=[],
            images=[],
            metadata={},
            source_file="test.pdf"
        )
        all_text = content.get_all_text()
        assert "Slide 1" in all_text
        assert "First" in all_text
        assert "Second" in all_text


class TestPDFExtractor:
    """Tests for PDF extractor."""

    def test_supported_extensions(self):
        """Test that PDF extensions are supported."""
        assert ".pdf" in PDFExtractor.SUPPORTED_EXTENSIONS

    def test_can_handle(self):
        """Test file type detection."""
        assert PDFExtractor.can_handle("lecture.pdf")
        assert not PDFExtractor.can_handle("lecture.pptx")

    @patch('lecture_study_guide.extractors.pdf_extractor.pdfplumber')
    def test_extract_basic(self, mock_pdfplumber):
        """Test basic PDF extraction."""
        # Mock PDF structure
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Test Title\nTest content"
        mock_page.extract_tables.return_value = []
        mock_page.images = []

        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.metadata = {"Title": "Test PDF"}

        mock_pdfplumber.open.return_value.__enter__.return_value = mock_pdf

        # Create temp file path
        with patch.object(Path, 'exists', return_value=True):
            extractor = PDFExtractor("test.pdf")
            content = extractor.extract()

            assert content.slide_count == 1
            assert "Test Title" in content.raw_text


class TestPowerPointExtractor:
    """Tests for PowerPoint extractor."""

    def test_supported_extensions(self):
        """Test that PPTX extensions are supported."""
        assert ".pptx" in PowerPointExtractor.SUPPORTED_EXTENSIONS
        assert ".ppt" in PowerPointExtractor.SUPPORTED_EXTENSIONS

    def test_can_handle(self):
        """Test file type detection."""
        assert PowerPointExtractor.can_handle("lecture.pptx")
        assert PowerPointExtractor.can_handle("lecture.ppt")
        assert not PowerPointExtractor.can_handle("lecture.pdf")
