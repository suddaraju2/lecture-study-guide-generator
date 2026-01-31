"""
Data models for study guide components.
"""

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum


class QuestionType(Enum):
    """Types of practice questions."""
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    TRUE_FALSE = "true_false"
    FILL_IN_BLANK = "fill_in_blank"
    ESSAY = "essay"


class Difficulty(Enum):
    """Difficulty levels for questions and concepts."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class Flashcard:
    """Represents a single flashcard for studying."""
    front: str
    back: str
    tags: list[str] = field(default_factory=list)
    source_slide: Optional[int] = None
    difficulty: Difficulty = Difficulty.MEDIUM

    def to_anki_format(self) -> str:
        """Convert to Anki import format (tab-separated)."""
        tags_str = " ".join(self.tags) if self.tags else ""
        return f"{self.front}\t{self.back}\t{tags_str}"

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "front": self.front,
            "back": self.back,
            "tags": self.tags,
            "source_slide": self.source_slide,
            "difficulty": self.difficulty.value
        }


@dataclass
class PracticeQuestion:
    """Represents a practice question with answer."""
    question: str
    answer: str
    question_type: QuestionType
    options: list[str] = field(default_factory=list)  # For multiple choice
    explanation: str = ""
    source_content: str = ""
    difficulty: Difficulty = Difficulty.MEDIUM
    topic: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "question": self.question,
            "answer": self.answer,
            "type": self.question_type.value,
            "options": self.options,
            "explanation": self.explanation,
            "difficulty": self.difficulty.value,
            "topic": self.topic
        }


@dataclass
class Concept:
    """Represents a key concept from the lecture."""
    name: str
    definition: str
    related_concepts: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)
    source_slide: Optional[int] = None
    importance: Difficulty = Difficulty.MEDIUM  # How important to study

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "definition": self.definition,
            "related_concepts": self.related_concepts,
            "examples": self.examples,
            "source_slide": self.source_slide,
            "importance": self.importance.value
        }


@dataclass
class ConceptMapNode:
    """A node in a concept map."""
    id: str
    label: str
    concept_type: str = "concept"  # concept, example, definition


@dataclass
class ConceptMapEdge:
    """An edge connecting two concepts."""
    source_id: str
    target_id: str
    relationship: str  # e.g., "is-a", "has", "leads-to", "example-of"


@dataclass
class ConceptMap:
    """Represents relationships between concepts."""
    title: str
    nodes: list[ConceptMapNode] = field(default_factory=list)
    edges: list[ConceptMapEdge] = field(default_factory=list)

    def to_mermaid(self) -> str:
        """Export as Mermaid diagram syntax."""
        lines = ["graph TD"]

        # Add nodes with labels
        for node in self.nodes:
            safe_label = node.label.replace('"', "'")
            lines.append(f'    {node.id}["{safe_label}"]')

        # Add edges with relationships
        for edge in self.edges:
            safe_rel = edge.relationship.replace('"', "'")
            lines.append(f'    {edge.source_id} -->|{safe_rel}| {edge.target_id}')

        return "\n".join(lines)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON export."""
        return {
            "title": self.title,
            "nodes": [{"id": n.id, "label": n.label, "type": n.concept_type} for n in self.nodes],
            "edges": [{"source": e.source_id, "target": e.target_id, "relationship": e.relationship} for e in self.edges]
        }


@dataclass
class ContentSection:
    """A section of extracted content."""
    title: str
    content: str
    slide_number: Optional[int] = None
    timestamp: Optional[str] = None  # For video lectures
    key_points: list[str] = field(default_factory=list)
    content_density: float = 0.5  # 0-1, how dense/important the content is


@dataclass
class StudyGuide:
    """Complete study guide generated from lecture materials."""
    title: str
    source_file: str
    summary: str = ""
    sections: list[ContentSection] = field(default_factory=list)
    concepts: list[Concept] = field(default_factory=list)
    flashcards: list[Flashcard] = field(default_factory=list)
    practice_questions: list[PracticeQuestion] = field(default_factory=list)
    concept_map: Optional[ConceptMap] = None
    review_priorities: list[str] = field(default_factory=list)  # Areas to focus on

    def to_dict(self) -> dict:
        """Convert entire study guide to dictionary."""
        return {
            "title": self.title,
            "source_file": self.source_file,
            "summary": self.summary,
            "sections": [
                {
                    "title": s.title,
                    "content": s.content,
                    "slide_number": s.slide_number,
                    "key_points": s.key_points,
                    "content_density": s.content_density
                }
                for s in self.sections
            ],
            "concepts": [c.to_dict() for c in self.concepts],
            "flashcards": [f.to_dict() for f in self.flashcards],
            "practice_questions": [q.to_dict() for q in self.practice_questions],
            "concept_map": self.concept_map.to_dict() if self.concept_map else None,
            "review_priorities": self.review_priorities
        }
