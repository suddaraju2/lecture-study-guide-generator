"""Tests for data models."""

import pytest
from lecture_study_guide.models import (
    Flashcard,
    PracticeQuestion,
    Concept,
    ConceptMap,
    ConceptMapNode,
    ConceptMapEdge,
    QuestionType,
    Difficulty
)


class TestFlashcard:
    """Tests for Flashcard model."""

    def test_create_flashcard(self):
        """Test creating a basic flashcard."""
        card = Flashcard(
            front="What is Python?",
            back="A high-level programming language",
            tags=["programming", "python"]
        )
        assert card.front == "What is Python?"
        assert card.back == "A high-level programming language"
        assert len(card.tags) == 2

    def test_to_anki_format(self):
        """Test Anki export format."""
        card = Flashcard(
            front="Question",
            back="Answer",
            tags=["tag1", "tag2"]
        )
        anki_str = card.to_anki_format()
        assert "Question\tAnswer\ttag1 tag2" == anki_str

    def test_to_dict(self):
        """Test dictionary conversion."""
        card = Flashcard(
            front="Q",
            back="A",
            tags=["test"],
            difficulty=Difficulty.HARD
        )
        d = card.to_dict()
        assert d["front"] == "Q"
        assert d["back"] == "A"
        assert d["difficulty"] == "hard"


class TestPracticeQuestion:
    """Tests for PracticeQuestion model."""

    def test_multiple_choice(self):
        """Test creating multiple choice question."""
        q = PracticeQuestion(
            question="Which is a programming language?",
            answer="A",
            question_type=QuestionType.MULTIPLE_CHOICE,
            options=["Python", "Banana", "Table", "Cloud"],
            explanation="Python is a programming language"
        )
        assert q.question_type == QuestionType.MULTIPLE_CHOICE
        assert len(q.options) == 4

    def test_to_dict(self):
        """Test dictionary conversion."""
        q = PracticeQuestion(
            question="Is Python interpreted?",
            answer="True",
            question_type=QuestionType.TRUE_FALSE
        )
        d = q.to_dict()
        assert d["type"] == "true_false"


class TestConcept:
    """Tests for Concept model."""

    def test_create_concept(self):
        """Test creating a concept."""
        concept = Concept(
            name="Recursion",
            definition="A function that calls itself",
            related_concepts=["Function", "Stack"],
            examples=["Factorial", "Fibonacci"]
        )
        assert concept.name == "Recursion"
        assert len(concept.related_concepts) == 2


class TestConceptMap:
    """Tests for ConceptMap model."""

    def test_to_mermaid(self):
        """Test Mermaid diagram generation."""
        nodes = [
            ConceptMapNode(id="n1", label="Parent"),
            ConceptMapNode(id="n2", label="Child")
        ]
        edges = [
            ConceptMapEdge(source_id="n1", target_id="n2", relationship="has")
        ]
        concept_map = ConceptMap(
            title="Test Map",
            nodes=nodes,
            edges=edges
        )

        mermaid = concept_map.to_mermaid()
        assert "graph TD" in mermaid
        assert 'n1["Parent"]' in mermaid
        assert "n1 -->|has| n2" in mermaid

    def test_to_dict(self):
        """Test dictionary conversion."""
        concept_map = ConceptMap(
            title="Test",
            nodes=[ConceptMapNode(id="n1", label="Test")],
            edges=[]
        )
        d = concept_map.to_dict()
        assert d["title"] == "Test"
        assert len(d["nodes"]) == 1
