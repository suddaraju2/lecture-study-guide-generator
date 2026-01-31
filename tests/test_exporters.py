"""Tests for exporters."""

import pytest
import tempfile
from pathlib import Path

from lecture_study_guide.models import (
    Flashcard,
    PracticeQuestion,
    Concept,
    StudyGuide,
    ContentSection,
    QuestionType,
    Difficulty
)
from lecture_study_guide.exporters import AnkiExporter, MarkdownExporter, JSONExporter


class TestAnkiExporter:
    """Tests for Anki exporter."""

    def test_export_txt(self):
        """Test TXT export for Anki."""
        cards = [
            Flashcard(front="Q1", back="A1", tags=["test"]),
            Flashcard(front="Q2", back="A2", tags=["test", "important"])
        ]

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            path = Path(f.name)

        try:
            AnkiExporter.export_txt(cards, path)
            content = path.read_text()

            assert "Q1\tA1\ttest" in content
            assert "Q2\tA2\ttest important" in content
        finally:
            path.unlink()

    def test_export_csv(self):
        """Test CSV export for Anki."""
        cards = [
            Flashcard(front="Question", back="Answer", tags=["tag"])
        ]

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            path = Path(f.name)

        try:
            AnkiExporter.export_csv(cards, path)
            content = path.read_text()

            assert "Front" in content
            assert "Question" in content
            assert "Answer" in content
        finally:
            path.unlink()


class TestMarkdownExporter:
    """Tests for Markdown exporter."""

    def test_export_study_guide(self):
        """Test Markdown export of study guide."""
        guide = StudyGuide(
            title="Test Guide",
            source_file="test.pdf",
            summary="This is a test summary.",
            sections=[
                ContentSection(
                    title="Introduction",
                    content="Intro content",
                    slide_number=1,
                    key_points=["Point 1", "Point 2"]
                )
            ],
            concepts=[
                Concept(
                    name="Test Concept",
                    definition="A test definition",
                    related_concepts=["Other"],
                    examples=["Example 1"]
                )
            ],
            flashcards=[
                Flashcard(front="Q", back="A")
            ],
            practice_questions=[
                PracticeQuestion(
                    question="What is this?",
                    answer="A test",
                    question_type=QuestionType.SHORT_ANSWER
                )
            ],
            review_priorities=["Study more"]
        )

        with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as f:
            path = Path(f.name)

        try:
            MarkdownExporter.export(guide, path)
            content = path.read_text()

            assert "# Test Guide" in content
            assert "This is a test summary" in content
            assert "Test Concept" in content
            assert "What is this?" in content
        finally:
            path.unlink()


class TestJSONExporter:
    """Tests for JSON exporter."""

    def test_export_and_load(self):
        """Test JSON export and reload."""
        guide = StudyGuide(
            title="JSON Test",
            source_file="test.pdf",
            summary="Test summary"
        )

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            path = Path(f.name)

        try:
            JSONExporter.export(guide, path)
            loaded = JSONExporter.load(path)

            assert loaded["title"] == "JSON Test"
            assert loaded["summary"] == "Test summary"
        finally:
            path.unlink()
