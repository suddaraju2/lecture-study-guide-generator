"""
Lecture Study Guide Generator
============================

A comprehensive tool that converts lecture recordings, slides, and documents
into study materials including study guides, practice questions, concept maps,
and Anki-compatible flashcards.

Usage:
    from lecture_study_guide import StudyGuideGenerator

    generator = StudyGuideGenerator(api_key="your-api-key")
    guide = generator.generate("lecture_slides.pptx")
    guide.export_all("output_folder/")
"""

from .core import StudyGuideGenerator
from .models import StudyGuide, Flashcard, ConceptMap, PracticeQuestion

__version__ = "1.0.0"
__author__ = "Your Name"
__all__ = [
    "StudyGuideGenerator",
    "StudyGuide",
    "Flashcard",
    "ConceptMap",
    "PracticeQuestion"
]
